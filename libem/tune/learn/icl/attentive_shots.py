"""
Attentive Shots

1. Training pass: Identify and record errors from the first training pass,
   labeling these as "mistakes."
2. Chain of thought retraining: Apply a chain-of-thought prompting to retrain
   Libem on just the mistakes, marking successfully resolved instances as "corrected."
3. Few-shot prompting: Use the corrected examples to enhance the few-shot learning prompts,
   improving model training and generalization.
"""

from typing import Iterable
from libem.core.struct import Prompt, Shot


def run(shots: Iterable[Shot],
        question: str,
        num_shots: int) -> Prompt.Shots:
    raise NotImplementedError
