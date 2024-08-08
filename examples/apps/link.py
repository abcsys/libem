import random

import libem
from libem.prepare.datasets.linking import febrl
from libem.optimize import cost


def main():
    random.seed(1)
    num_samples = 10

    print("Loading data...")
    df_a, df_b = febrl.load(num_samples=num_samples)
    df_a_test = df_a.drop(columns=["rec_id"])
    df_b_test = df_b.drop(columns=["rec_id"])

    libem.calibrate({
        "libem.match.prompt.rules": "soc_sec_id distinguishes individuals"
    })
    with libem.trace as t:
        df_link = libem.link(df_a_test, df_b_test)

    print(f"Given:\n{df_a}\nAnd:\n{df_b}")
    print(f"After linking:\n{df_link.sort_values(by=['__cluster__'])}")

    print("Stats:")
    stats = t.stats()
    libem.pprint({
        "task_completion_time": libem.round(t.duration()),
        "throughput": libem.round((len(df_a) + len(df_b)) / t.duration()),
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
