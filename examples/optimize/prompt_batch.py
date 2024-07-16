import libem

from libem.core import model
from libem.optimize import profile
from libem.prepare.datasets import abt_buy


def main():
    samples, num_samples = [], 10
    samples = []

    dataset = abt_buy.read_test()
    for _ in range(num_samples):
        samples.append(next(dataset))

    print("Without batch:")
    libem.calibrate({
        "libem.match.parameter.sync": True,
        "libem.match.parameter.batch_size": 1,
    })
    no_batch_results = profile(samples)
    libem.pprint(no_batch_results)
    print()

    model.reset_client()

    print("With batch:")
    libem.calibrate({
        "libem.match.parameter.sync": True,
        "libem.match.parameter.batch_size": 5,
    })
    batch_results = profile(samples)
    libem.pprint(batch_results)

    print()
    f1_loss = libem.round(no_batch_results["f1"] - batch_results["f1"], 2)
    speedup = libem.round(no_batch_results["latency"] / batch_results["latency"], 2)
    cost_savings = libem.round(no_batch_results["cost"] - batch_results["cost"], 2)

    print(f"F1 loss: {f1_loss}")
    print(f"Speedup: {speedup}x")
    print(f"Cost savings: ${cost_savings}")


if __name__ == "__main__":
    main()
