import libem
from libem.core import eval
from libem.optimize.cost import openai

schema = {}


def func():
    pass


def profile(dataset):
    with libem.trace as t:
        preds, truths = [], []
        for i, record in enumerate(dataset):
            print(f"[profile] pair #{i + 1}\n")

            left, right, truth = record["left"], record["right"], record["label"]

            pred = libem.match(left, right)["answer"]

            preds.append(1 if pred.lower() == "yes" else 0)
            truths.append(truth)

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

    return {
        "f1": f1,
        "precision": p,
        "recall": r,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "tn": tn,
        **stats,
    }
