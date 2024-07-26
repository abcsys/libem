import time
from typing import Iterable

import libem
from libem.core import eval
from libem.optimize.cost import openai

schema = {}


def func():
    pass


def profile(dataset: Iterable, num_samples=-1, detailed=False):
    with libem.trace as t:
        preds, truths = [], []

        left, right = [], []
        for i, record in enumerate(dataset):
            left.append(str(record["left"]))
            right.append(str(record["right"]))
            truths.append(record["label"])

            if num_samples > 0 and i >= num_samples:
                break

        start = time.time()
        preds = [
            1 if is_match["answer"].lower() == "yes" else 0
            for is_match in libem.match(left, right)
        ]
        latency = time.time() - start

        f1 = eval.f1(truths, preds)
        p = eval.precision(truths, preds)
        r = eval.recall(truths, preds)
        tp, fp, tn, fn = eval.confusion_matrix(truths, preds)

    stats = t.stats()
    stats["model"]["cost"] = openai.get_cost(
        libem.parameter.model(),
        num_input_tokens=stats["model"]["num_input_tokens"]["sum"],
        num_output_tokens=stats["model"]["num_output_tokens"]["sum"],
    )

    if detailed:
        return {
            "f1": f1,
            "precision": p,
            "recall": r,
            "latency": latency,
            "throughput": len(left) / latency,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "tn": tn,
            **stats,
        }
    else:
        return {
            "f1": round(f1, 2),
            "precision": round(p, 2),
            "recall": round(r, 2),
            "latency": latency,
            "throughput": round(len(left) / latency, 2),
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "tn": tn,
            "num_model_calls": stats["model"]["num_model_calls"]["sum"],
            "num_input_tokens": stats["model"]["num_input_tokens"]["sum"],
            "num_output_tokens": stats["model"]["num_output_tokens"]["sum"],
            "cost": stats["model"]["cost"],
        }
