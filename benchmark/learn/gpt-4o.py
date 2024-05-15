import argparse
import benchmark
import libem
from libem.core.struct import Prompt

def main(args):
    
    # set model-specific config
    args.model = 'gpt-4o'
    libem.calibrate({
        "libem.match.prompt.rule":
            Prompt(default=Prompt.Rule(rules=[])),
        "libem.match.prompt.experience":
            Prompt(
                default=Prompt.Experience(mistakes=["Compare the titles of both entities carefully, focusing on specific keywords and phrases to ensure they refer to the same product version or edition.",
                    'Check for differences in product versions, editions, or specific features mentioned in the titles (e.g., "full version" vs. "upgrade").',
                    "Verify the manufacturer information when available; mismatches in manufacturer names can indicate different products.",
                    "Consider significant price differences as a potential indicator of different products, especially if the price difference is substantial.",
                    'Look for additional details in the titles that may differentiate the products, such as "academic," "OEM," "complete package," or specific user licenses.',
                    "Pay attention to product codes or model numbers in the titles, as these can help identify whether the products are the same or different.",
                    'Check for specific platform or operating system mentions (e.g., "Mac," "Windows") to ensure compatibility and product matching.',
                    'Be cautious of products with similar names but different purposes or target audiences (e.g., "security suite" vs. "protection suite").',
                    'Ensure that any additional descriptors in the titles (e.g., "deluxe," "professional," "standard") match between the entities.',
                    'Consider the context of the product usage (e.g., "server" vs. "desktop" versions) to determine if they are the same product.',
                    'Look for any mention of packaging or included items (e.g., "DVD," "CD") that might differentiate the products.',
                    "Verify if the product is an upgrade or a full version, as these are often different products.",
                    'Check for any specific licensing terms mentioned (e.g., "unlimited users," "1 year subscription") that could indicate different products.',
                    'Ensure that any software version numbers (e.g., "v6.0," "v8.0") match between the entities.',
                    "Consider the release year or version year mentioned in the titles to ensure they refer to the same product version.",
                    "Be aware of any additional product features or bundled items mentioned in the titles that could differentiate the products.",
                    'Check for any specific regional or language versions mentioned (e.g., "French") that might indicate different products.',
                    'Ensure that any product-specific terms (e.g., "academic," "education") match between the entities.',
                    "Consider the overall context and combination of title, manufacturer, and price to make a final determination on product matching."]),
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