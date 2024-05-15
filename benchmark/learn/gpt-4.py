import argparse
import benchmark
import libem
from libem.core.struct import Prompt

def main(args):
    
    # set model-specific config
    args.model = 'gpt-4'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=Prompt.Rule(rules=[])),
        "libem.match.prompt.experience":
            Prompt(
                default=Prompt.Experience(mistakes=[
                                    'Consider version compatibility and '
                                    'specificity when matching software '
                                    'titles.  ',
                                    'Ensure exact match or clear equivalence '
                                    'in product descriptions before confirming '
                                    'a match.  ',
                                    'Verify that the product type (e.g., '
                                    'upgrade, deluxe, standard) matches '
                                    'exactly between entities.  ',
                                    'Check for platform compatibility (e.g., '
                                    'Windows vs. Mac) in software titles.  ',
                                    'Match manufacturer names accurately, '
                                    'and do not assume a match when the '
                                    'manufacturer is unspecified in one '
                                    'entity.  ',
                                    'Consider the context and usage of the '
                                    'product (e.g., academic, professional, '
                                    'personal) when matching.  ',
                                    'Do not rely solely on price similarity '
                                    'to determine a match; significant price '
                                    'differences often indicate different '
                                    'products or packages.  ',
                                    'Be cautious with numerical versions and '
                                    'editions; ensure they exactly match or '
                                    'are contextually appropriate (e.g., '
                                    'version 2.0 vs. deluxe 2.0).  ',
                                    'Pay attention to licensing terms and '
                                    'durations (e.g., 1-year vs. 3-year '
                                    'licenses) as they can differentiate '
                                    'products.  ',
                                    'Ensure that additional descriptors like '
                                    '"complete package" or "media only" are '
                                    'considered in the matching '
                                    'process.',]),
            )
        })

    benchmark.benchmark(args)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser("benchmark.py")
    parser.add_argument("--dataset", dest='dataset', nargs='?', help="The dataset to benchmark.", type=str,
                        default='amazon-google')
    parser.add_argument("--num_pair", dest='num_pair', nargs='?',
                        help="Number of pairs to run through. Set as 0 to run through the entire dataset.", type=int,
                        default=5)
    parser.add_argument("--start", dest='start', nargs='?', help="The index of the dataset to start from.", type=int, 
                        default=0)
    parser.add_argument("--file", dest='file', nargs='?', help="Name of the file to save to, will append '.json'.", 
                        type=str, default='')
    parser.add_argument("--no_schema", dest='schema', help="Turn off the dataset schema.",
                        action='store_true', default=True)
    parser.add_argument("--no_shuffle", dest='shuffle', help="Don't shuffle the dataset.", action='store_true', 
                        default=True)
    parser.add_argument("--verbose", dest='verbose', help="Print intermediate results for each pair to console.", 
                        action='store_true', default=False)
    parser.add_argument("--browse", dest='browse', help="Enable the browse tool.", 
                        action='store_true', default=False)
    
    args = parser.parse_args()
    main(args)