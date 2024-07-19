# similarity thresholds for blocking to
# achieve 100% recall
block_similarities = {
    'abt-buy': 29,
    'amazon-google': 54,
    'beer': 79,
    'dblp-acm': 79,
    'dblp-scholar': 59,
    'fodors-zagats': 83,
    'itunes-amazon': 63,
    'walmart-amazon': 50
}

from benchmark.classic import (
    abt_buy,
    amazon_google,
    beer,
    dblp_acm,
    dblp_scholar,
    fodors_zagats,
    itunes_amazon,
    walmart_amazon,
    challenging,
)
