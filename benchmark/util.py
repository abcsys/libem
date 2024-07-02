import os
import sys
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime

import libem
from libem.optimize.cost import openai
from libem.core.eval import confusion_matrix, precision, recall, f1
from libem.core.struct import Prompt
from libem.match.parameter import tools


def benchmark(dataset, args):
    total_start_time = time.time()

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
        dataset, stats['block'], results['block'] = benchmark_block(dataset, args)
    if args.match:
        stats['match'], results['match'] = benchmark_match(dataset, args)
    stats['total_latency'] = round(time.time() - total_start_time, 2)

    if args.log:
        # save results to ./results
        results_folder = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'results')
        Path(results_folder).mkdir(parents=True, exist_ok=True)

        if args.output_file:
            output_file = os.path.join(results_folder, f'{args.output_file}.json')
        else:
            signature = [
                datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
                args.name
            ]
            if args.block:
                signature.append('block')
            if args.match:
                signature.append(args.model)
                signature.append(str(args.num_pairs if args.num_pairs > 0 else 'all'))
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
            output_file = os.path.join(results_folder, f'{"-".join(signature)}.json')

        with open(output_file, 'w') as f:
            json.dump({
                'command': sys.argv[1:],
                'stats': stats,
                'results': results,
                'configs': libem.config(),
            }, f, indent=4)

        print(f"Benchmark: Results saved to: {output_file}")


def benchmark_block(dataset, args):
    total_pairs = len(dataset['left']) * len(dataset['right'])

    print(f"Benchmark: Blocking {total_pairs} potential pairs from the {args.name} benchmark", end='')
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


def benchmark_match(dataset, args):
    total_start_time = time.time()
    truth, predictions, results = [], [], []
    total_input_tokens, total_output_tokens = 0, 0

    print(f"Benchmark: Matching {args.num_pairs if args.num_pairs > 0 else 'all'} "
          f"{'pair' if args.num_pairs == 1 else 'pairs'} "
          f"from the {args.name} benchmark:")
    for i, data in enumerate(dataset[args.start_index:]):
        if i + 1 < args.start_index:
            continue

        e1 = data['left']
        e2 = data['right']
        label = data['label']

        if not args.quiet:
            print(f"Pair #{i + 1}\n")
            print(f"Entity 1: {e1}\n")
            print(f"Entity 2: {e2}")

        # call match
        with libem.trace as t:
            is_match = None
            start_time = time.time()

            while is_match is None:
                # retry if model times out
                num_timeouts = 0
                try:
                    is_match = libem.match(e1, e2)
                except libem.ModelTimedoutException:
                    num_timeouts += 1

            if num_timeouts > 0:
                print(f"Model timed out {num_timeouts} time(s).")

            # get unparsed model output and telemetry
            latency = time.time() - start_time

            model_output = [i['match']['model_output'] for i in t.get() if 'match' in i]
            model_output = model_output[0] if model_output else None

            input_tokens = sum([
                i['model']['num_input_tokens'] for i in t.get() if 'model' in i
            ])
            output_tokens = sum([
                i['model']['num_output_tokens'] for i in t.get() if 'model' in i
            ])

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            # append results
            results.append({
                'entity_1': e1,
                'entity_2': e2,
                'label': label,
                'pred': is_match["answer"],
                'confidence': is_match["confidence"],
                'explanation': is_match["explanation"],
                'model_output': model_output,
                'tools_used': [i['tool'] for i in t.get() if 'tool' in i],
                'latency': round(latency, 2),
                'tokens': {
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens,
                    'cost': openai.get_cost(
                        args.model, input_tokens, output_tokens
                    )
                }
            })

        # track results for evaluation metrics
        if is_match["answer"] == 'yes':
            predictions.append(1)
        else:
            predictions.append(0)
        truth.append(label)

        if not args.quiet:
            print()
            print(f"Match: {is_match['answer']}; "
                  f"Confidence: {is_match['confidence']}; "
                  f"Label: {label}\n")

        # check num_pairs stop condition
        if args.num_pairs > 0 and i - args.start_index + 1 >= args.num_pairs:
            break

    # generate stats
    metrics = [precision, recall, f1]
    conf_mat = confusion_matrix(np.array(truth), np.array(predictions))
    stats = {
        m.__name__:
            round(m(np.array(truth), np.array(predictions)) * 100, 2)
        for m in metrics
    }
    stats['latency'] = round(time.time() - total_start_time, 2)
    stats['tokens'] = {
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens,
        'cost': openai.get_cost(
            args.model,
            total_input_tokens,
            total_output_tokens
        )
    }
    stats['confusion_matrix'] = {
        'tp': int(conf_mat[0]),
        'fp': int(conf_mat[1]),
        'tn': int(conf_mat[2]),
        'fn': int(conf_mat[3])
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
