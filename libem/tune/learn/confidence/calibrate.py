import numpy as np
from scipy.optimize import minimize
from sklearn.metrics import log_loss


def temperature_scale(confidence_scores, labels) -> list[float]:
    if len(confidence_scores) == 0:
        return confidence_scores

    labels = np.array(labels)
    if len(np.unique(labels)) == 1:
        return confidence_scores

    confidence_scores = np.array(confidence_scores)

    epsilon = 1e-15
    confidence_scores = np.clip(confidence_scores, epsilon, 1 - epsilon)
    logits = np.log(confidence_scores / (1 - confidence_scores))

    def temperature_scaling_loss(T):
        scaled_logits = logits / T

        calibrated_scores = 1 / (1 + np.exp(-scaled_logits))
        return log_loss(labels, calibrated_scores)

    # Optimize temperature parameter
    result = minimize(temperature_scaling_loss,
                      x0=np.array([1.0]),
                      bounds=[(0.1, 10.0)])
    optimal_temperature = result.x[0]

    # Apply the optimal temperature to the logits
    calibrated_logits = logits / optimal_temperature
    calibrated_confidence_scores = 1 / (1 + np.exp(-calibrated_logits))

    return list(calibrated_confidence_scores)


if __name__ == "__main__":
    initial_confidence_scores = np.array([0.9, 0.75, 0.6, 0.4, 0.3])
    labels = np.array([1, 1, 0, 0, 0])
    calibrated_confidence_scores = temperature_scale(initial_confidence_scores, labels)
    print("Initial Confidence Scores:", initial_confidence_scores)
    print("Calibrated Confidence Scores:", calibrated_confidence_scores)
