"""
interview_analyzer.py

Analyzes:
- Emotion
- Emotion Confidence
- Head Pose

Generates interview feedback.

Used by:
    interview_camera.py
"""


def analyze_interview(emotion, confidence, pitch, yaw, roll):
    """
    Analyze interview data and generate feedback.

    Parameters
    ----------
    emotion : str
        Detected emotion label

    confidence : float
        Emotion confidence (0-100)

    pitch : float
        Head pitch angle

    yaw : float
        Head yaw angle

    roll : float
        Head roll angle

    Returns
    -------
    dict
        Dictionary containing interview analysis.
    """

    feedback = []

    # -----------------------------------
    # Emotion Analysis
    # -----------------------------------

    positive_emotions = [
        "happy",
        "neutral",
        "surprise"
    ]

    negative_emotions = [
        "angry",
        "sad",
        "fear",
        "disgust"
    ]

    emotion_lower = emotion.lower()

    if emotion_lower in positive_emotions:
        feedback.append("Good facial expression.")

    elif emotion_lower in negative_emotions:
        feedback.append("Try to maintain a calm and positive expression.")

    else:
        feedback.append("Maintain a confident facial expression.")

    # -----------------------------------
    # Confidence Analysis
    # -----------------------------------

    if confidence >= 90:
        feedback.append("Emotion detected with very high confidence.")

    elif confidence >= 70:
        feedback.append("Emotion detected confidently.")

    else:
        feedback.append("Face visibility could be improved.")

    # -----------------------------------
    # Head Pose Analysis
    # -----------------------------------

    if pitch is not None:

        if pitch > 15:
            feedback.append("Lower your chin slightly.")

        elif pitch < -15:
            feedback.append("Raise your head slightly.")

    if yaw is not None:

        if yaw > 20:
            feedback.append("Look more towards the camera.")

        elif yaw < -20:
            feedback.append("Look more towards the camera.")

    if roll is not None:

        if roll > 15:
            feedback.append("Keep your head straight.")

        elif roll < -15:
            feedback.append("Keep your head straight.")

    # -----------------------------------
    # Overall Score
    # -----------------------------------

    score = 100

    if emotion_lower in negative_emotions:
        score -= 20

    if confidence < 70:
        score -= 10

    if pitch is not None and abs(pitch) > 15:
        score -= 10

    if yaw is not None and abs(yaw) > 20:
        score -= 10

    if roll is not None and abs(roll) > 15:
        score -= 10

    if score < 0:
        score = 0

    # -----------------------------------
    # Return Analysis
    # -----------------------------------

    return {
        "emotion": emotion,
        "confidence": round(confidence, 2),
        "pitch": None if pitch is None else round(pitch, 2),
        "yaw": None if yaw is None else round(yaw, 2),
        "roll": None if roll is None else round(roll, 2),
        "score": score,
        "feedback": feedback
    }