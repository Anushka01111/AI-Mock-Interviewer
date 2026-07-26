"""
emotion_detector.py

Emotion prediction helper.

Works with:
- PIL Images
- OpenCV Frames (after conversion)
"""

import torch

from app.pipeline.emotional_model import processor, model


def predict_emotion(image):
    """
    Predict emotion from a PIL Image.

    Returns:
        emotion
        confidence
        emotion_scores
    """

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():

        outputs = model(**inputs)

    probabilities = torch.nn.functional.softmax(
        outputs.logits,
        dim=1
    )

    confidence, predicted_class = torch.max(
        probabilities,
        dim=1
    )

    emotion = model.config.id2label[
        predicted_class.item()
    ]

    emotion_scores = {}

    for index, score in enumerate(probabilities[0]):

        label = model.config.id2label[index]

        emotion_scores[label] = score.item()

    # ------------------------------------
    # Confidence Threshold
    # ------------------------------------

    THRESHOLD = 0.70

    confidence = confidence.item()

    if confidence < THRESHOLD:
        emotion = "uncertain"

    return (
        emotion,
        confidence,
        emotion_scores
    )