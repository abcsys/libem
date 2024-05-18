import argparse
import benchmark
import libem
from libem.core.struct import Prompt

def main(args):
    # set dataset-specific config
    args.dataset = "amazon-google"
    libem.calibrate({
        "libem.match.prompt.query": "Do the two product descriptions refer to the same real-world product? "
                                    "Answer with 'Yes' if they do and 'No' if they do not.\n"
                                    "Product 1: '{left}'\nProduct 2: '{right}'",
        "libem.match.prompt.rule": Prompt.Rule(),
        "libem.match.prompt.experience": Prompt.Experience(),
        "libem.match.prompt.output": ""
        })

    benchmark.benchmark(args)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--model", dest='model', nargs='?', help="The OpenAI model to use.", 
                        type=str, default='gpt-4-turbo')
    parser.add_argument("--num_pair", dest='num_pair', nargs='?',
                        help="Number of pairs to run through. Set as 0 to run through the entire dataset.", 
                        type=int, default=5)
    parser.add_argument("--start", dest='start', nargs='?', help="The index of the dataset to start from.", 
                        type=int, default=0)
    parser.add_argument("--file", dest='file', nargs='?', help="Name of the file to save to, will append '.json'.", 
                        type=str, default='')
    parser.add_argument("--no_schema", dest='schema', help="Turn off the dataset schema.",
                        action='store_false', default=True)
    parser.add_argument("--no_shuffle", dest='shuffle', help="Don't shuffle the dataset.", 
                        action='store_false', default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.", 
                        action='store_true', default=False)
    parser.add_argument("--browse", dest='browse', help="Enable the browse tool.", 
                        action='store_true', default=False)
    
    args = parser.parse_args()
    main(args)