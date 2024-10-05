import libem

from libem.optimize import profile
from libem.prepare.datasets import abt_buy


def main():
    samples, num_samples = [], 5
    samples = []

    dataset = abt_buy.read_test()
    for _ in range(num_samples):
        samples.append(next(dataset))

    print("Synchronous execution:")
    libem.calibrate({
        "libem.match.parameter.sync": True,
    })
    before = profile(samples)
    libem.pprint(before)
    print()

    print("Asynchronous execution:")
    libem.calibrate({
        "libem.match.parameter.sync": False,
    })
    after = profile(samples)
    libem.pprint(after)
    print()

    speedup = libem.round(before["latency"] / after["latency"], 2)

    print(f"Speedup: {speedup}x")


if __name__ == "__main__":
    main()
