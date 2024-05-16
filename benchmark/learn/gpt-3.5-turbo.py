import argparse
import benchmark
import libem
from libem.core.struct import Prompt

def main(args):
    
    # set model-specific config
    args.model = 'gpt-3.5-turbo-0613'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=Prompt.Rule(rules=[
                                    'Match entities if titles are similar, '
                                    'disregarding minor differences such as '
                                    'punctuation, order of words, and presence '
                                    'of version numbers.',
                                    '',
                                    'Consider entities as matching if the '
                                    'manufacturer is the same or if one entity '
                                    'lacks a manufacturer but other details '
                                    'align closely.',
                                    '',
                                    'Treat entities with very close prices '
                                    '(within a small percentage threshold) as '
                                    'potentially matching, especially if other '
                                    'details like title or manufacturer '
                                    'align.',
                                    '',
                                    'Do not match entities based solely on '
                                    'similar titles if the product versions or '
                                    'editions are different, particularly for '
                                    'software.',
                                    '',
                                    'Ignore minor price differences when '
                                    'other factors like title and manufacturer '
                                    'strongly suggest a match.',
                                    '',
                                    'Consider entities as non-matching if '
                                    'there is a significant price difference '
                                    'unless there is overwhelming evidence '
                                    'from other attributes (like exact title '
                                    'and manufacturer match).',
                                    '',
                                    'Do not assume entities are the same if '
                                    'one mentions a specific feature or '
                                    'component (like "upgrade" or "bundle") '
                                    'that the other does not, unless all other '
                                    'information matches.',
                                    '',
                                    'Entities with different primary '
                                    'functions or intended uses (e.g., '
                                    'different types of software or different '
                                    'editions) should not be matched, even if '
                                    'titles are similar.',
                                    '',
                                    'Use caution when matching entities with '
                                    'and without manufacturer details; ensure '
                                    'other attributes like title and price are '
                                    'very closely aligned.',
                                    '',
                                    'When in doubt, prioritize title and '
                                    'manufacturer similarity over price, '
                                    'especially for high-value items where '
                                    'price variations can be larger.',])),
        "libem.match.prompt.experience":
            Prompt(
                default=Prompt.Experience(mistakes=[]),
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