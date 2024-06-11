import os
import sys
import json
import numpy as np
import time
import argparse
import ast
from pathlib import Path
from datetime import datetime

import libem
from libem.tune.optimize.cost import openai
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

    truth, predictions, result = [], [], []
    total_input_tokens, total_output_tokens = 0, 0

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

            input_tokens = sum([i['model']['num_input_tokens'] for i in t.get() if 'model' in i])
            output_tokens = sum([i['model']['num_output_tokens'] for i in t.get() if 'model' in i])
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            # append results
            result.append({
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

    # save results to ./results
    results_folder = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'results')
    Path(results_folder).mkdir(parents=True, exist_ok=True)

    if args.output_file:
        output_file = os.path.join(results_folder, f'{args.output_file}.json')
    else:
        signature = [
            datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            args.name, args.model, str(args.num_pairs if args.num_pairs > 0 else 'all'),
        ]
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

    # get stats
    metrics = [precision, recall, f1]
    conf_mat = confusion_matrix(np.array(truth), np.array(predictions))
    stats = {m.__name__: round(m(np.array(truth), np.array(predictions)) * 100, 2) for m in metrics}
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
        'tn': int(conf_mat[2]),
        'fp': int(conf_mat[1]),
        'fn': int(conf_mat[3])
    }

    with open(output_file, 'w') as f:
        json.dump({
            'command': sys.argv[1:],
            'stats': stats,
            'results': result,
            'configs': libem.config(),
        }, f, indent=4)

    print(f"Benchmark: Done {len(truth)} matches in {stats['latency']}s.")
    print(f"Benchmark: Precision\t {stats['precision']}")
    print(f"Benchmark: Recall\t {stats['recall']}")
    print(f"Benchmark: F1 score\t {stats['f1']}")
    print(f"Benchmark: Cost \t ${stats['tokens']['cost']}")
    print(f"Benchmark: Results saved to: {output_file}")


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
