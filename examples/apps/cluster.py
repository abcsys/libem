import random

import libem
from libem.prepare.datasets.clustering import febrl
from libem.optimize import cost

from libem.cluster import eval


def main():
    random.seed(1)
    num_samples = 15

    df = febrl.load_test()
    df = df.head(num_samples)
    df = df.sample(frac=1).reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)

    with libem.trace as t:
        df_predict = libem.cluster(df_test)
    t.stats()

    stats = t.stats()
    stats["model"]["cost"] = cost.get_cost(
        libem.parameter.model(),
        num_input_tokens=stats["model"]["num_input_tokens"]["sum"],
        num_output_tokens=stats["model"]["num_output_tokens"]["sum"],
    )

    print("Given:")
    print(df_test)

    print("After clustering:")
    print(df_predict.sort_values(by='cluster_id').reset_index(drop=True))

    print("Stats:")
    libem.pprint({
        **eval(df["cluster_id"], df_predict["cluster_id"]),
        "task_completion_time": libem.round(t.duration()),
        "throughput": libem.round(len(df_test) / t.duration()),
        "num_model_calls": stats["model"]["num_model_calls"]["sum"],
        "num_input_tokens": stats["model"]["num_input_tokens"]["sum"],
        "num_output_tokens": stats["model"]["num_output_tokens"]["sum"],
        "cost": stats["model"]["cost"],
    })


if __name__ == '__main__':
    main()
