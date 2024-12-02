import time
import math
import numpy as np
import libem
from libem.core import eval
from libem.optimize import cost as cost_util
from libem.tune.learn.confidence.calibrate import temperature_scale
from libem.match import prompt as match_prompt
from libem.match import digest as match_digest

from libem.core.struct import Shots, Shot

def stage_filter(results, threshold=0.5):
    low_confidence_pairs = []
    high_confidence_results = []

    for result in results:
        pred = result["pred"]
        confidence = result['confidence']
        if confidence is not None and confidence < threshold:
            low_confidence_pairs.append({
                'left': result['left'],
                'right': result['right'],
                'label': result['label']
            })
        else:
            high_confidence_results.append(result)
            
    return low_confidence_pairs, high_confidence_results


def run(train_set, test_set, args):
    num_pairs = len(test_set)
    num_batches = math.ceil(num_pairs / args.batch_size)

    print(f"Cascading: Matching {num_pairs} "
          f"{'pair' if num_pairs == 1 else 'pairs'} "
          f"{f'in {num_batches} batches ' if args.batch_size > 1 else ''}"
          f"using {args.model}"
          f"from the {args.name} dataset.")

    if args.num_shots > 0:
        shots = Shots([
            Shot(
                question=match_prompt.query(left=d['left'], right=d['right']),
                answer="yes" if d['label'] == 1 else "no"
            ) for d in train_set
        ])
        print(f"Cascading: Using {args.num_shots} shots with {args.icl} strategy "
              f"for in-context learning.")
    else:
        shots = []

    start_time = time.time()

    results = {}

    with libem.trace as t:
        libem.calibrate({
            "libem.match.parameter.batch_size": args.batch_size,
            "libem.match.parameter.sync": args.sync,
            "libem.match.prompt.shots": shots,
        })

        if args.sync and args.batch_size == 1:
            print("Cascading: Running in synchronous mode with batch size 1.")
            # iterate and match each pair
            for i, data in enumerate(test_set):
                if 0 < args.num_pairs < i + 1:
                    break

                left, right = data['left'], data['right']
                label = data['label']
                
                if not args.quiet:
                    print(f"Pair #{i + 1}\n")
                    print(f"Entity 1: {left}\n")
                    print(f"Entity 2: {right}")

                num_retries = 0
                while True:
                    try:
                        is_match: dict = libem.match(left, right)
                        results[match_digest(left, right)] = {
                            'left': left,
                            'right': right,
                            'label': label,
                            'pred': is_match['answer'],
                            'confidence': is_match['confidence'],
                            'explanation': is_match['explanation'],
                        }

                        if not args.quiet:
                            print(f"Match: {is_match['answer']}; "
                                  f"Confidence: {is_match['confidence']}; "
                                  f"Label: {label}\n")
                        break
                    except libem.ModelTimedoutException:
                        num_retries += 1
                        print(f"Retrying {num_retries} time(s) "
                              f"due to model call timeout..")
        else:
            # prepare datasets
            print("Cascading: Running in asynchronous mode.")
            left, right, labels = [], [], []
            for i, data in enumerate(test_set):

                if 0 < args.num_pairs < i + 1:
                    break

                left.append(data['left'])
                right.append(data['right'])
                labels.append(data['label'])

            answers: list[dict] = libem.match(left, right)

            results = {
                match_digest(l, r): {
                    'left': l,
                    'right': r,
                    'label': label,
                    'pred': is_match['answer'],
                    'confidence': is_match['confidence'],
                    'explanation': is_match['explanation'],
                }
                for l, r, label, is_match in zip(left, right, labels, answers)
            }

        # fill in additional info from the trace
        for span in t.get():
            if 'match' not in span:
                continue

            match = span['match']
            left, right = match['left'], match['right']

            # for batch matching, the trace are
            # shared between pairs in each batch
            if isinstance(left, list):
                pass
            else:
                left, right = [left], [right]

            for l, r in zip(left, right):
                digest = match_digest(l, r)
                model_usage = match['model_usage']
                results[digest].update(
                    {
                        'model_output': match['model_output'],
                        'tool_outputs': match['tool_outputs'],
                        'latency': libem.round(match['latency'], 2),
                        'tokens': {
                            'num_input_tokens': model_usage['num_input_tokens'],
                            'num_output_tokens': model_usage['num_output_tokens'],
                            'cost': libem.round(cost_util.get_cost(
                                args.model,
                                model_usage['num_input_tokens'],
                                model_usage['num_output_tokens'],
                            ), 4)
                        }
                    }
                )
        end_time = time.time()

        # ignore the digest key
        results = list(results.values())

    truth = [result['label'] for result in results]
    predictions = [1 if result['pred'] == 'yes' else 0 for result in results]
    latencies = [result['latency'] for result in results]
    confidences = [result['confidence'] for result in results if result['confidence'] is not None]
    print(f"Model: {args.model}")
    if args.model != "gpt-4o":
        print(f"Calibrating confidences for model: {args.model}")
        calibrated_confidences = temperature_scale(confidences, truth)
        results = patch_calibrated_confidence(results, calibrated_confidences)

    # generate stats
    metrics = eval.report(
        truth, predictions
    )
    telemetry = t.telemetry(flatten=True)

    stats = {
        'num_pairs': num_pairs,
        'precision': round(metrics['precision'] * 100, 2),
        'recall': round(metrics['recall'] * 100, 2),
        'f1': round(metrics['f1'] * 100, 2),
        'latency': round(end_time - start_time, 2),
        'throughput': libem.round(num_pairs / (end_time - start_time), 2),
        'accuracy': round(metrics['accuracy'] * 100, 2),
        'per_pair_latency': libem.round((end_time - start_time) / num_pairs, 2),
        'avg_batch_latency': libem.round(np.mean(latencies), 2),
        'avg_confidence': libem.round(np.mean(confidences), 2) if confidences else -1,
        'tokens': {
            'num_input_tokens': telemetry['model.num_input_tokens']['sum'],
            'num_output_tokens': telemetry['model.num_output_tokens']['sum'],
            'cost': libem.round(cost_util.get_cost(
                args.model,
                telemetry['model.num_input_tokens']['sum'],
                telemetry['model.num_output_tokens']['sum'],
            ), 4)
        },
        'confusion_matrix': {
            'tp': metrics['tp'],
            'fp': metrics['fp'],
            'tn': metrics['tn'],
            'fn': metrics['fn'],
        }
    }

    print(f"Cascading: Matching done in {stats['latency']}s.")
    if not args.quiet:
        print(f"Benchmark: Precision\t {stats['precision']}")
        print(f"Benchmark: Recall\t {stats['recall']}")
        print(f"Benchmark: F1 score\t {stats['f1']}")
        print(f"Benchmark: Throughput\t {stats['throughput']} pps")
        print(f"Benchmark: Cost \t ${stats['tokens']['cost']}")

    return stats, results


def patch_calibrated_confidence(results, calibrated_confidences):
    for i, result in enumerate(results):
        if result['confidence'] is not None:
            results[i] = place_to_next(
                result, 'confidence', 'calibrated_confidence',
                round(calibrated_confidences[i], 2)
                if result['confidence'] is not None else None
            )
    return results


def place_to_next(d, key_next_to, key_to_place, value_to_place):
    new_dict = dict()

    for key, value in d.items():
        new_dict[key] = value
        if key == key_next_to:
            new_dict[key_to_place] = value_to_place

    return new_dict


def profile(args, results, num_pairs):
    truth = [result['label'] for result in results]
    predictions = [1 if result['pred'] == 'yes' else 0 for result in results]
    latencies = [result['latency'] for result in results]
    confidences = [result['confidence'] for result in results if result['confidence'] is not None]

    # generate stats
    metrics = eval.report(
        truth, predictions
    )

    stats = {
        'num_pairs': num_pairs,
        'precision': round(metrics['precision'] * 100, 2),
        'recall': round(metrics['recall'] * 100, 2),
        'f1': round(metrics['f1'] * 100, 2),
        'accuracy': round(metrics['accuracy'] * 100, 2),
        'avg_batch_latency': libem.round(np.mean(latencies), 2),
        'avg_confidence': libem.round(np.mean(confidences), 2) if confidences else -1,
        'confusion_matrix': {
            'tp': metrics['tp'],
            'fp': metrics['fp'],
            'tn': metrics['tn'],
            'fn': metrics['fn'],
        }
    }

    return stats