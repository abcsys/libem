import argparse
import benchmark
import libem
from libem.core.struct import Prompt

def main(args):
    
    # set model-specific config
    args.model = 'gpt-4-turbo'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=Prompt.Rule(rules=[
                'Consider version and edition differences explicitly, even if titles are similar.',
                    'Check for specific product types like upgrades, licenses, or bundles, and do not assume they are the same as standalone products.',
                    'Validate that the product intended for the same platform (e.g., Windows, Mac) before matching.',
                    'Ensure that the product titles match closely, avoiding mismatches due to additional descriptors that change the product context (e.g., family pack, professional edition).',
                    'Do not match products based solely on the presence of similar keywords; context and completeness of the title are crucial.',
                    'Compare manufacturer names if available; absence in one entity does not immediately imply a match with an entity having a manufacturer.',
                    'Price differences can be indicative of different products or versions; significant price discrepancies likely mean different products.',
                    'Consider the release context, such as software version numbers or edition years, to ensure both products are indeed the same.',
                    'Avoid matching products where one is a specific type of service or subscription unless explicitly stated in both entities.',
                    'Be cautious with products that have similar names but may differ in content or intended use, such as educational versions versus professional versions.',
                    'Acknowledge the presence of additional terms like "deluxe," "premium," or "professional" as they typically denote different product tiers.',
                    'Do not assume products are the same based on partial title matches; ensure all major elements of the product title align.',
                    'For software, consider the implications of different licensing terms or durations mentioned in the titles.',
                    'When in doubt, err on the side of not matching unless all key aspects (title, manufacturer, version, price) align closely.'])),
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