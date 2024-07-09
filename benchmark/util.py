import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

import libem
from libem.core import eval
from libem.core.struct import Prompt
from libem.optimize.cost import openai
from libem.match.parameter import tools
from libem.match import digest as match_digest


def benchmark(dataset, args):
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
            "libem.match.prompt.rules": Prompt.Rules(args.rules),
        })

    results, stats = {}, {}
    if args.block:
        dataset, stats['block'], results['block'] = run_block(dataset, args)
    if args.match:
        stats['match'], results['match'] = run_match(dataset, args)
    stats['total_latency'] = round(time.time() - start_time, 2)

    if args.log:
        # save results to ./results
        results_folder = os.path.join(
            os.path.split(os.path.abspath(__file__))[0],
            'results'
        )
        Path(results_folder).mkdir(parents=True, exist_ok=True)

        if args.output_file:
            output_file = os.path.join(
                results_folder,
                f'{args.output_file}.json'
            )
        else:
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
            if args.train:
                signature.append('train')
            if not args.schema:
                signature.append('no-schema')
            if args.cot:
                signature.append('cot')
            if args.guess:
                signature.append('guess')
            if args.rules:
                signature.append('rules')
            output_file = os.path.join(
                results_folder, f'{"-".join(signature)}.json'
            )

        with open(output_file, 'w') as f:
            json.dump({
                'command': sys.argv[1:],
                'stats': stats,
                'results': results,
                'configs': libem.config(),
            }, f, indent=4)

        print(f"Benchmark: Results saved to: {output_file}")


def run_block(dataset, args):
    total_pairs = len(dataset['left']) * len(dataset['right'])

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
    block_iter = libem.block(dataset['left'], dataset['right'])
    block_next = next(block_iter, None)
    while block_next:
        blocked.append(block_next)

        # check num_pairs stop condition
        if args.num_pairs > 0 and len(blocked) - args.start_index >= args.num_pairs:
            break

        block_next = next(block_iter, None)
    total_time = time.time() - start_time

    # generate output and stats
    out = []
    tp, fp, fn, num_tn = [], [], [], 0
    for pair in blocked:
        if pair in dataset['true']:
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

    for pair in dataset['true']:
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


def run_match(dataset, args):
    start_time = time.time()

    results = {}
    truth, predictions, = [], []

    print(f"Benchmark: Matching {args.num_pairs if args.num_pairs > 0 else 'all'} "
          f"{'pair' if args.num_pairs == 1 else 'pairs'} "
          f"from the {args.name} benchmark:")

    with libem.trace as t:
        start_index = max(args.start_index or 0, 0)

        if args.batch_size == 1:
            # iterate over dataset
            for i, data in enumerate(dataset[start_index:]):
                if args.num_pairs > 0 and i + 1 > args.num_pairs:
                    break

                left = data['left']
                right = data['right']
                label = data['label']

                if not args.quiet:
                    print(f"Pair #{i + 1}\n")
                    print(f"Entity 1: {left}\n")
                    print(f"Entity 2: {right}")

                num_retries = 0
                while True:
                    try:
                        is_match = libem.match(left, right)
                        results[match_digest(left, right)] = {
                            'left': left,
                            'right': right,
                            'label': label,
                            'pred': is_match['answer'],
                            'confidence': is_match['confidence'],
                            'explanation': is_match['explanation'],
                        }

                        predictions.append(
                            1 if is_match['answer'] == 'yes' else 0
                        )
                        truth.append(label)

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
            # batch matching
            libem.calibrate({
                "libem.match.parameter.batch_size": args.batch_size,
                "libem.match.parameter.quiet": args.quiet,
            })

            # prepare datasets
            left, right, labels = [], [], []
            for i, data in enumerate(dataset[start_index:]):
                if args.num_pairs > 0 and i + 1 > args.num_pairs:
                    break

                left.append(data['left'])
                right.append(data['right'])
                labels.append(data['label'])

            answers: list[dict] = libem.match(left, right)

            results = {}
            for l, r, label, is_match in \
                    zip(left, right, labels, answers):
                results[match_digest(l, r)] = {
                    'left': l,
                    'right': r,
                    'label': label,
                    'pred': is_match['answer'],
                }

                predictions.append(
                    1 if is_match['answer'] == 'yes' else 0
                )
                truth.append(label)

        # fill in additional info from the trace
        for span in t.get():
            if not 'match' in span:
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
                        'latency': round(match['latency'], 2),
                        'tokens': {
                            'num_input_tokens': model_usage['num_input_tokens'],
                            'num_output_tokens': model_usage['num_output_tokens'],
                            'cost': openai.get_cost(
                                args.model,
                                model_usage['num_input_tokens'],
                                model_usage['num_output_tokens'],
                            )
                        }
                    }
                )
        # ignore the digest key
        results = list(results.values())

    # generate stats
    metrics = eval.report(
        truth, predictions
    )
    telemetry = t.telemetry(flatten=True)

    stats = {
        'precision': round(metrics['precision'] * 100, 2),
        'recall': round(metrics['recall'] * 100, 2),
        'f1': round(metrics['f1'] * 100, 2),
        'latency': round(time.time() - start_time, 2),
        'tokens': {
            'num_input_tokens': telemetry['model.num_input_tokens']['sum'],
            'num_output_tokens': telemetry['model.num_output_tokens']['sum'],
            'cost': openai.get_cost(
                args.model,
                telemetry['model.num_input_tokens']['sum'],
                telemetry['model.num_output_tokens']['sum'],
            )
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
    print(f"Benchmark: Cost \t ${stats['tokens']['cost']}")

    return stats, results


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
