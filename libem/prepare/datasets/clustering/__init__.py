from libem.prepare.datasets.clustering import (
    febrl,
    amazon_google,
    dblp_scholar,
    itunes_amazon,
)

datasets = {
    'febrl': febrl.load_raw,
    'amazon-google': amazon_google.load_raw,
    'dblp-scholar': dblp_scholar.load_raw,
    'itunes-amazon': itunes_amazon.load_raw,
}