import numpy as np


def precision(truth, predictions):
    """
    Calculate the precision of predictions:
    Precision = True Positives / (True Positives + False Positives)

    Parameters:
    truth (array-like): Actual ground truths (boolean or binary).
    predictions (array-like): Predictions made by the model (boolean or binary).

    Returns:
    float: The precision of the predictions. If there are no positive predictions,
           returns 1 if there are also no true positives (perfect precision), otherwise 0.
    """
    truth = np.asarray(truth, dtype=bool)
    predictions = np.asarray(predictions, dtype=bool)
    if np.sum(predictions) == 0:
        return 1 if np.sum(truth) == 0 else 0
    return np.sum(truth & predictions) / np.sum(predictions)


def recall(truth, predictions):
    """
    Calculate the recall of predictions:
    Recall = True Positives / (True Positives + False Negatives)

    Parameters:
    truth (array-like): Actual ground truths (boolean or binary).
    predictions (array-like): Predictions made by the model (boolean or binary).

    Returns:
    float: The recall of the predictions. If there are no true positives,
           returns 1 if there are also no positive predictions (perfect recall), otherwise 0.
    """
    truth = np.asarray(truth, dtype=bool)
    predictions = np.asarray(predictions, dtype=bool)
    if np.sum(truth) == 0:
        return 1 if np.sum(predictions) == 0 else 0
    return np.sum(truth & predictions) / np.sum(truth)


def f1(truth, predictions):
    """
    Calculate the F1 score of predictions:
    F1 Score = 2 * (Precision * Recall) / (Precision + Recall)

    Parameters:
    truth (array-like): Actual ground truths (boolean or binary).
    predictions (array-like): Predictions made by the model (boolean or binary).

    Returns:
    float: The F1 score. If both precision and recall are zero, returns 0.
    """
    truth = np.asarray(truth, dtype=bool)
    predictions = np.asarray(predictions, dtype=bool)
    p = precision(truth, predictions)
    r = recall(truth, predictions)
    if p + r == 0:
        return 0
    return 2 * p * r / (p + r)


def accuracy(truth, predictions):
    """
    Calculate the accuracy of predictions:
    Accuracy = (True Positives + True Negatives) / Total

    Parameters:
    truth (array-like): Actual ground truths (boolean or binary).
    predictions (array-like): Predictions made by the model (boolean or binary).

    Returns:
    float: The accuracy of the predictions.
    """
    truth = np.asarray(truth, dtype=bool)
    predictions = np.asarray(predictions, dtype=bool)
    return np.sum(truth == predictions) / len(truth)


def confusion_matrix(truth, predictions):
    """
    Calculate the confusion matrix for binary classification:

    - True Positive (TP): Correctly predicted positive observations
    - False Positive (FP): Incorrectly predicted as positive
    - True Negative (TN): Correctly predicted negative observations
    - False Negative (FN): Incorrectly predicted as negative

    Parameters:
    truth (array-like): Actual ground truths (boolean or binary).
    predictions (array-like): Predictions made by the model (boolean or binary).

    Returns:
    tuple: Returns a tuple containing the counts of TP, FP, TN, and FN.
    """
    truth = np.asarray(truth, dtype=bool)
    predictions = np.asarray(predictions, dtype=bool)

    # True Positives: Truth and predictions are both True
    tp = np.sum(truth & predictions)

    # False Positives: Predictions are True, but truth is False
    fp = np.sum(predictions & ~truth)

    # True Negatives: Both truth and predictions are False
    tn = np.sum(~truth & ~predictions)

    # False Negatives: Predictions are False, but truth is True
    fn = np.sum(~predictions & truth)

    return int(tp), int(fp), int(tn), int(fn)


def report(truth: np.array, predictions: np.array):
    tp, fp, tn, fn = confusion_matrix(
        truth, predictions
    )
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision(truth, predictions),
        "recall": recall(truth, predictions),
        "f1": f1(truth, predictions),
        "accuracy": accuracy(truth, predictions),
    }
