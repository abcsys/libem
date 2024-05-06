import numpy as np


def precision(truth, predictions):
    return np.sum(truth & predictions) / np.sum(predictions)


def recall(truth, predictions):
    return np.sum(truth & predictions) / np.sum(truth)


def f1(truth, predictions):
    p = precision(truth, predictions)
    r = recall(truth, predictions)
    return 2 * p * r / (p + r)


def accuracy(truth, predictions):
    return np.sum(truth == predictions) / len(truth)


def confusion_matrix(truth, predictions):
    tp = np.sum(truth & predictions)
    fp = np.sum(predictions & ~truth)
    tn = np.sum(~truth & ~predictions)
    fn = np.sum(~predictions & truth)
    return tp, fp, tn, fn
