import libem
from libem.core import eval
from libem.optimize.cost import openai
from libem.match import parameter as match_param

schema = {}


def func():
    pass


def profile(dataset, detailed=False):
    with libem.trace as t:
        preds, truths = [], []

        # batch
        if match_param.batch_size() > 1:
            left, right = [], []
            for i, record in enumerate(dataset):
                left.append(record["left"])
                right.append(record["right"])
                truths.append(record["label"])
            preds = [
                1 if is_match["answer"].lower() == "yes" else 0
                for is_match in libem.match(left, right)
            ]
        # no batch
        else:
            for i, record in enumerate(dataset):
                print(f"[profile] pair #{i + 1}")

                pred = libem.match(
                    record["left"], record["right"]
                )["answer"]
                
                preds.append(1 if pred.lower() == "yes" else 0)
                truths.append(record["label"])

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
            "fp": fp,
            "fn": fn,
            "tp": tp,
            **stats,
        }
    else:
        return {
            "f1": round(f1, 2),
            "precision": round(p, 2),
            "recall": round(r, 2),
            "num_model_calls": stats["model"]["num_model_calls"]["sum"],
            "num_input_tokens": stats["model"]["num_input_tokens"]["sum"],
            "num_output_tokens": stats["model"]["num_output_tokens"]["sum"],
            "latency": round(stats["match"]["latency"]["sum"], 2),
            "cost": stats["model"]["cost"],
        }
