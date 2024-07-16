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
    sync_results = profile(samples)
    libem.pprint(sync_results)
    print()

    libem.reset()

    print("Asynchronous execution:")
    libem.calibrate({
        "libem.match.parameter.sync": False,
    })
    async_results = profile(samples)
    libem.pprint(async_results)

    print()
    speedup = libem.round(sync_results["latency"] / async_results["latency"], 2)

    print(f"Speedup: {speedup}x")


if __name__ == "__main__":
    main()
