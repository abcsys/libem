from libem.prepare.datasets.linking import amazon_google
from libem.optimize import profile
import libem


def main():
    batch_size = 10
    left, right, mapping = amazon_google.load()
    libem.calibrate({
        "libem.block.parameter.similarity": 54,
        "libem.match.parameter.batch_size": batch_size,
    })

    # geet all possible matches for the first 5 records in the left dataset
    results = libem.block(left[0:10], right, ignore=["id", "description", "price"])
    
    dataset, matching = [], 0
    # format the dataset by removing "id" and adding "label"
    for res in results:
        pair = {"left": {k: v for k, v in res["left"].items() if k != "id"}, 
                "right": {k: v for k, v in res["right"].items() if k != "id"},}
        
        if {res["left"]["id"], res["right"]["id"]} in mapping:
            pair["label"] = 1
            matching += 1
        else:
            pair["label"] = 0
        dataset.append(pair)
    
    print(f"Total pairs: {len(dataset)}, # matching pairs: {matching}, batch size: {batch_size}")
    
    # normal batching
    print("Normal batching:")
    libem.calibrate({
        "libem.match.parameter.record_batch": False,
    })
    normal = profile(dataset)
    libem.pprint(normal)
    print()
    
    # record batching
    print("Record batching:")
    libem.calibrate({
        "libem.match.parameter.record_batch": True,
    })
    record = profile(dataset)
    libem.pprint(record)
    
    print()

    f1_diff = libem.round(record["f1"] - normal["f1"], 2)
    speedup = libem.round(normal["latency"] / record["latency"], 2)
    cost_savings = libem.round(normal["cost"] - record["cost"], 2)
    cost_percent = libem.round((cost_savings / normal["cost"]) * 100, 2)

    print(f"F1 difference: {f1_diff}")
    print(f"Speedup: {speedup}x")
    print(f"Cost savings: ${cost_savings} ({cost_percent}%)")


if __name__ == '__main__':
    main()
