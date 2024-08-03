# similarity thresholds for blocking to
# achieve 100% recall
block_similarities = {
    'abt-buy': 50,
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

classic_benchmarks = {
    'abt-buy': abt_buy.run,
    'amazon-google': amazon_google.run,
    'beer': beer.run,
    'dblp-acm': dblp_acm.run,
    'dblp-scholar': dblp_scholar.run,
    'fodors-zagats': fodors_zagats.run,
    'itunes-amazon': itunes_amazon.run,
    'walmart-amazon': walmart_amazon.run,
}

challenges = {
    'classic.challenging': challenging.run,
}

benchmarks = {
    **classic_benchmarks,
    **challenges,
}
