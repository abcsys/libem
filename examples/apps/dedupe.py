import random

import libem
from libem.prepare.datasets.clustering import febrl
from libem.optimize import cost


def main():
    random.seed(1)
    num_samples = 15

    df = febrl.load_test() \
        .head(num_samples) \
        .sample(frac=1) \
        .reset_index(drop=True)
    df_test = df.drop(["cluster_id"], axis=1)

    with libem.trace as t:
        df_dedupe = libem.dedupe(df_test)

    print(f"Given:\n{df_test}")
    print(f"After deduplication:\n{df_dedupe}")

    print("Stats:")
    stats = t.stats()
    libem.pprint({
        "task_completion_time": libem.round(t.duration()),
        "throughput": libem.round(len(df_test) / t.duration()),
        "num_model_calls": stats["model"]["num_model_calls"]["sum"],
        "num_input_tokens": stats["model"]["num_input_tokens"]["sum"],
        "num_output_tokens": stats["model"]["num_output_tokens"]["sum"],
        "cost": cost.get_cost(
            libem.parameter.model(),
            num_input_tokens=stats["model"]["num_input_tokens"]["sum"],
            num_output_tokens=stats["model"]["num_output_tokens"]["sum"],
        ),
    })


if __name__ == '__main__':
    main()
