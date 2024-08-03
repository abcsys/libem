import os
import time
import pprint as pp
import pandas as pd
from datetime import datetime

import benchmark as bm
import libem
from benchmark import run

name = os.path.basename(__file__).replace(".py", "")


def run_benchmark():
    datasets = bm.classic_benchmarks.keys()

    args = run.args()
    args.model = "gpt-4-turbo"
    args.num_pairs = -1
    args.log = False

    start = time.time()

    reports = {}
    for dataset in datasets:
        args.name = dataset

        print(f"Running {dataset}...")
        print(args)

        libem.reset()
        report = run.run(args)
        reports[dataset] = report["stats"]

    pp.pprint(reports, sort_dicts=False)
    print(f"Total time: {time.time() - start:.2f}s")

    return reports


def report_to_dataframe(reports):
    rows = []
    for dataset, report in reports.items():
        match = report["match"]
        rows.append({
            "dataset": dataset,
            "num_pairs": match["num_pairs"],
            "precision": match["precision"],
            "recall": match["recall"],
            "f1": match["f1"],
            "accuracy": match["accuracy"],
            "latency": match["latency"],
            "throughput": match["throughput"],
            "per_pair_latency": match["per_pair_latency"],
            "avg_batch_latency": match["avg_batch_latency"],
            "avg_confidence": match["avg_confidence"],
            "num_input_tokens": match["tokens"]["num_input_tokens"],
            "num_output_tokens": match["tokens"]["num_output_tokens"],
            "cost": match["tokens"]["cost"],
            "tp": match["confusion_matrix"]["tp"],
            "fp": match["confusion_matrix"]["fp"],
            "tn": match["confusion_matrix"]["tn"],
            "fn": match["confusion_matrix"]["fn"],
        })

    return pd.DataFrame(rows)


def tabulate(df: pd.DataFrame):
    df.to_markdown(os.path.join(
        bm.table_dir,
        f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
        f"{name}.md"),
        index=False
    )


def plot(df: pd.DataFrame):
    pass


def save(df: pd.DataFrame):
    df.to_csv(os.path.join(
        bm.result_dir,
        f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-"
        f"{name}.csv"),
        index=False)


def show(df: pd.DataFrame):
    print(df)


if __name__ == "__main__":
    reports = run_benchmark()

    df = report_to_dataframe(reports)
    save(df)

    df = df[["dataset", "precision", "recall", "f1",
             "cost", "throughput"]]
    field_names = {
        "dataset": "Dataset",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1",
        "cost": "Cost ($)",
        "throughput": "Throughput (pps)",
    }
    df = df.rename(columns=field_names)
    tabulate(df)
    plot(df)
    show(df)
