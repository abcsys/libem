import libem
from libem.core import util as libem_util

schema = {}


def func(*args, **kwargs):
    raise NotImplementedError


def predict(dataset) -> tuple[list, list, list, list]:
    preds, truths = [], []
    mistakes, successes = [], []

    # TBD avoid forcing pair-wise prediction
    for i, record in enumerate(dataset):
        left, right, truth = str(record["left"]), \
                             str(record["right"]), \
                             record["label"]

        pred = libem.match(left, right)["answer"]
        libem.info("[predict] record:", i, "pred:", pred, "true:", truth)

        preds.append(1 if pred.lower() == "yes" else 0)
        truths.append(truth)

        truth = "yes" if truth == 1 else "no"
        outcome = {
            "entity 1": left,
            "entity 2": right,
            "your answer": pred,
            "true answer": truth,
        }

        if pred == truth:
            successes.append(outcome)
        else:
            mistakes.append(outcome)
    return preds, truths, mistakes, successes


def check(dataset, metric: str = "libem.core.eval.f1") -> tuple[float, list]:
    preds, truths, mistakes, successes = predict(dataset)
    metric_func = libem_util.get_func(metric)
    score = metric_func(preds, truths)

    libem.info("[check] metric:", metric, "score:", score)
    return score, mistakes
