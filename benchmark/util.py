import os
import sys
import math
import time
import json
import argparse
import numpy as np
from datetime import datetime
from typing import Iterable

import libem
from libem.core import eval
from libem.core.struct import Rules
from libem.match.parameter import tools
from libem.match import digest as match_digest
from libem.match import prompt as match_prompt
from libem.optimize import cost as cost_util
from libem.tune.learn.confidence.calibrate import temperature_scale
from libem.tune.learn import icl_strategies
from libem.core.struct import Shots, Shot

from benchmark.classic import block_similarities
import benchmark as bm


def benchmark(train_set: Iterable,
              test_set: Iterable,
              args: argparse.Namespace) -> dict:
    start_time = time.time()

    if args.quiet:
        libem.quiet()
    if args.debug:
        libem.debug_on()

    if args.guess:
        libem.calibrate({
            "libem.parameter.guess": True,
        })
    if args.browse:
        libem.calibrate({
            "libem.match.parameter.tools": tools + ["libem.browse"],
        })
    if args.model:
        libem.calibrate({
            "libem.match.parameter.model": args.model,
        })
    if args.temperature:
        libem.calibrate({
            "libem.match.parameter.temperature": args.temperature,
        })
    if args.cot:
        libem.calibrate({
            "libem.match.parameter.cot": True,
        })
    if args.confidence:
        libem.calibrate({
            "libem.match.parameter.confidence": True,
        })
    if args.rules:
        libem.calibrate({
            "libem.match.prompt.rules": Rules(args.rules),
        })
    if args.icl:
        libem.calibrate({
            "libem.match.parameter.icl_strategy": icl_strategies[args.icl],
        })
    if args.num_shots:
        libem.calibrate({
            "libem.match.parameter.num_shots": args.num_shots,
        })

    results, stats = {}, {}

    # blocking
    if args.block:
        test_set, stats['block'], results['block'] = run_block(test_set, args)

    # matching
    if args.match:
        stats['match'], results['match'] = run_match(train_set, test_set, args)

    stats['total_latency'] = round(time.time() - start_time, 2)

    report = {
        'command': sys.argv[1:],
        'stats': stats,
        'results': results,
        'configs': libem.config(),
    }

    if args.log:
        signature = create_signature(args)

        if args.output_file:
            output_file = os.path.join(
                bm.result_dir,
                f'{args.output_file}.json'
            )
        else:
            output_file = os.path.join(
                bm.result_dir,
                f'{"-".join(signature)}.json'
            )

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=4)

        print(f"Benchmark: Results saved to: {output_file}")

    return report


def run_block(test_set: Iterable, args: argparse.Namespace):
    libem.calibrate({
        "libem.block.parameter.similarity": args.similarity
        if 0 <= args.similarity <= 100
        else block_similarities[args.name]
    })

    # prepare the blocking dataset
    # deduplicate left and right descriptions
    left = [json.loads(i) for i in set(json.dumps(d['left']) for d in test_set)]
    right = [json.loads(i) for i in set(json.dumps(d['right']) for d in test_set)]
    true = [{'left': d['left'], 'right': d['right']}
            for d in test_set if d['label'] == 1]

    total_pairs = len(left) * len(right)

    print(f"Benchmark: Blocking {total_pairs} potential pairs "
          f"from the {args.name} benchmark", end='')
    if args.num_pairs > 0:
        print(f",\nBenchmark: stopping after the first "
              f"{'pair' if args.num_pairs == 1 else f'{args.num_pairs} pairs'} "
              f"that pass{f'es' if args.num_pairs == 1 else ''} the cutoff:")
    else:
        print(":")

    blocked = []
    start_time = time.time()
    for pair in libem.block(left, right):
        blocked.append(pair)

        # check num_pairs stop condition
        if 0 < args.num_pairs <= len(blocked) - args.start_index:
            break
    total_time = time.time() - start_time
    # generate output and stats
    out = []
    tp, fp, fn, num_tn = [], [], [], 0
    for pair in blocked:
        if pair in true:
            tp.append(pair)
            out.append({
                'left': pair['left'],
                'right': pair['right'],
                'label': 1
            })
        else:
            fp.append(pair)
            out.append({
                'left': pair['left'],
                'right': pair['right'],
                'label': 0
            })

    for pair in true:
        if pair not in tp:
            fn.append(pair)

    num_tn = total_pairs - len(tp) - len(fp) - len(fn)
    if len(tp) == 0:
        precision = 100 if len(fp) == 0 else 0
        recall = 100 if len(fn) == 0 else 0
    else:
        precision = len(tp) / (len(tp) + len(fp)) * 100
        recall = len(tp) / (len(tp) + len(fn)) * 100
    f1 = 0 if precision + recall == 0 \
        else 2 * round(precision * recall / (precision + recall), 2)

    stats = {
        'precision': round(precision, 2),
        'recall': round(recall, 2),
        'f1': f1,
        'latency': total_time,
        'confusion_matrix': {
            'tp': len(tp),
            'fp': len(fp),
            'tn': num_tn,
            'fn': len(fn)
        }
    }

    results = {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'tn': num_tn
    }

    print()
    print(f"Benchmark: Blocking done in {round(total_time, 2)}s.")
    if args.num_pairs <= 0 or args.num_pairs > len(out):
        print(f"Benchmark: Resulting pairs\t {len(out)}")
        print(f"Benchmark: Percent blocked\t {round((1 - len(out) / total_pairs) * 100, 2)}")
    print(f"Benchmark: Precision\t\t {stats['precision']}")
    print(f"Benchmark: Recall\t\t {stats['recall']}")
    print(f"Benchmark: F1 score\t\t {stats['f1']}")

    return out, stats, results


def run_match(train_set, test_set, args):
    test_set = list(test_set)

    if args.num_pairs > 0:
        num_pairs = min(args.num_pairs, len(test_set) - args.start_index)
    else:
        num_pairs = len(test_set) - args.start_index
    num_batches = math.ceil(num_pairs / args.batch_size)

    print(f"Benchmark: Matching {num_pairs} "
          f"{'pair' if num_pairs == 1 else 'pairs'} "
          f"{f'in {num_batches} batches ' if args.batch_size > 1 else ''}"
          f"from the {args.name} benchmark.")

    if args.num_shots > 0:
        shots = Shots([
            Shot(
                question=match_prompt.query(left=d['left'], right=d['right']),
                answer="yes" if d['label'] == 1 else "no"
            ) for d in train_set
        ])
        print(f"Benchmark: Using {args.num_shots} shots with {args.icl} strategy "
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
            # iterate and match each pair
            for i, data in enumerate(test_set[args.start_index:]):
                if 0 < args.num_pairs < i + 1:
                    break

                left, right = str(data['left']), str(data['right'])
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
            left, right, labels = [], [], []
            for i, data in enumerate(test_set[args.start_index:]):
                if 0 < args.num_pairs < i + 1:
                    break

                left.append(str(data['left']))
                right.append(str(data['right']))
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

    print()
    print(f"Benchmark: Matching done in {stats['latency']}s.")
    print(f"Benchmark: Precision\t {stats['precision']}")
    print(f"Benchmark: Recall\t {stats['recall']}")
    print(f"Benchmark: F1 score\t {stats['f1']}")
    print(f"Benchmark: Throughput\t {stats['throughput']} pps")
    print(f"Benchmark: Cost \t ${stats['tokens']['cost']}")

    return stats, results


def create_signature(args):
    signature = [
        datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
        args.name
    ]
    if args.block:
        signature.append('block')
    if args.batch_size > 1:
        signature.append(f'batch-{args.batch_size}')
    if args.match:
        signature.append(args.model)
        signature.append(
            str(args.num_pairs if args.num_pairs > 0 else 'all')
        )
    if not args.schema:
        signature.append('no-schema')
    if args.cot:
        signature.append('cot')
    if args.guess:
        signature.append('guess')
    if args.rules:
        signature.append('rules')

    return signature


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


def ordinal_suffix(num):
    # Special cases for 11th, 12th, 13th
    if 10 <= num % 100 <= 13:
        suffix = 'th'
    else:
        # Last digit of num
        last_digit = num % 10
        if last_digit == 1:
            suffix = 'st'
        elif last_digit == 2:
            suffix = 'nd'
        elif last_digit == 3:
            suffix = 'rd'
        else:
            suffix = 'th'
    return str(num) + suffix
