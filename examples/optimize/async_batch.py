import libem

from libem.optimize import profile
from libem.prepare.datasets import abt_buy


def main():
    samples, num_samples = [], 10
    samples = []

    dataset = abt_buy.read_test()
    for _ in range(num_samples):
        samples.append(next(dataset))

    print("Synchronous execution with batch size 1:")
    libem.calibrate({
        "libem.match.parameter.sync": True,
        "libem.match.parameter.batch_size": 1,
    })
    before = profile(samples)
    libem.pprint(before)
    print()

    print("Asynchronous execution with batch size 5:")
    libem.calibrate({
        "libem.match.parameter.sync": False,
        "libem.match.parameter.batch_size": 5,
    })
    after = profile(samples)
    libem.pprint(after)
    print()

    f1_loss = libem.round(before["f1"] - after["f1"], 2)
    speedup = libem.round(before["latency"] / after["latency"], 2)
    cost_savings = libem.round(before["cost"] - after["cost"], 2)

    print(f"F1 loss: {f1_loss}")
    print(f"Speedup: {speedup}x")
    print(f"Cost savings: ${cost_savings}")
    print()


if __name__ == "__main__":
    main()
