import os
import json
import argparse

from benchmark import result_dir, analysis_dir


def get_mistakes(input_file):
    with open(input_file) as f:
        results = json.load(f)
    fp_cases, fn_cases = [], []
    for case in results['results']['match']:
        if case['pred'] == 'yes' and case['label'] == 0:
            fp_cases.append(case)
        elif case['pred'] == 'no' and case['label'] == 1:
            fn_cases.append(case)
    return {
        "stats": {
            "fp": len(fp_cases),
            "fn": len(fn_cases),
        },
        "fp": fp_cases,
        "fn": fn_cases,
    }


def get_correct(input_file):
    with open(input_file) as f:
        results = json.load(f)
    tp_cases, tn_cases = [], []
    for case in results['results']['match']:
        if case['pred'] == 'yes' and case['label'] == 1:
            tp_cases.append(case)
        elif case['pred'] == 'no' and case['label'] == 0:
            tn_cases.append(case)
    return {
        "stats": {
            "tp": len(tp_cases),
            "tn": len(tn_cases),
        },
        "tp": tp_cases,
        "tn": tn_cases,
    }


def write(output_file, data):
    if not os.path.exists(analysis_dir):
        os.makedirs(analysis_dir)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Analysis results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("analysis")

    parser.add_argument("-i", "--input", dest='input_file', nargs='?',
                        help="Name of the file to read from.", type=str,
                        default='')
    parser.add_argument("-o", "--output", dest='output_file', nargs='?',
                        help="Name of the file to save to.", type=str,
                        default='')
    parser.add_argument("-m", "--mistake", dest='mistake',
                        help="Output mistakes.",
                        action='store_true', default=False)
    parser.add_argument("-c", "--correctness", dest='correct',
                        help="Output correct cases.",
                        action='store_true', default=False)
    parser.add_argument("-l", "--last", dest='last', nargs='?',
                        help="Use the nth newest result file.",
                        type=int, default=-1)
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    if not input_file:
        """Use the newest result file by default."""
        files = os.listdir(result_dir)
        files = [f for f in files if f.endswith('.json')]
        files = sorted(files, key=lambda x: os.path.getmtime(
            os.path.join(result_dir, x)))
        input_file = os.path.join(result_dir, files[args.last])

    """if input_file does not have directory, add result_dir"""
    if not os.path.exists(input_file):
        input_file = os.path.join(result_dir, input_file)

    if args.mistake:
        mistakes = get_mistakes(input_file)
        if not output_file:
            output_file = os.path.join(
                analysis_dir,
                f'{os.path.basename(input_file).split(".")[0]}'
                f'-mistakes.json'
            )
        write(output_file, mistakes)

    if args.correct:
        correct = get_correct(input_file)
        if not output_file:
            output_file = os.path.join(
                analysis_dir,
                f'{os.path.basename(input_file).split(".")[0]}'
                f'-correct.json'
            )
        write(output_file, correct)

    ...
