import os
import json
import argparse

_dir = os.path.dirname(os.path.realpath(__file__))
_result_dir = os.path.join(_dir, 'results')
_analysis_dir = os.path.join(_dir, 'analysis')


def get_mistakes(input_file):
    with open(input_file) as f:
        results = json.load(f)
    fp_cases, fn_cases = [], []
    for case in results['results']:
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


def write(output_file, data):
    if not os.path.exists(_analysis_dir):
        os.makedirs(_analysis_dir)
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
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    if not input_file:
        """Use the newest result file by default."""
        files = os.listdir(_result_dir)
        files = [f for f in files if f.endswith('.json')]
        files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(_result_dir, x)))
        input_file = os.path.join(_result_dir, files[-1])

    """if input_file does not have directory, add _result_dir"""
    if not os.path.exists(input_file):
        input_file = os.path.join(_result_dir, input_file)

    if args.mistake:
        mistakes = get_mistakes(input_file)
        if not output_file:
            output_file = os.path.join(
                _analysis_dir,
                f'{os.path.basename(input_file).split(".")[0]}'
                f'_mistakes.json'
            )
        write(output_file, mistakes)

    ...
