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

    print("Asynchronous execution with batch size 1:")
    libem.calibrate({
        "libem.match.parameter.sync": False,
        "libem.match.parameter.batch_size": 1,
    })
    sync_results = profile(samples)
    libem.pprint(sync_results)
    print()

    model.reset_client()

    print("Asynchronous execution with batch size 5:")
    libem.calibrate({
        "libem.match.parameter.sync": False,
        "libem.match.parameter.batch_size": 5,
    })
    async_results = profile(samples)
    libem.pprint(async_results)

    print()
    speedup = libem.round(sync_results["latency"] / async_results["latency"], 2)

    print(f"Speedup: {speedup}x")


if __name__ == "__main__":
    main()
