"""
answer_summary.py

Week 4

Collects frame-by-frame interview data and
generates an answer-level summary.

Stores:
- Emotion
- Confidence
- Pitch
- Yaw
- Roll
- Eye Contact

Returns:
- Emotion %
- Eye Contact %
- Average Pitch
- Average Yaw
- Average Roll
"""

from collections import Counter


class AnswerSummary:

    def __init__(self):

        self.emotions = []
        self.confidences = []

        self.pitch_values = []
        self.yaw_values = []
        self.roll_values = []

        self.eye_contact_frames = 0
        self.total_frames = 0

    # -----------------------------------------
    # Add One Frame
    # -----------------------------------------

    def add_frame(
        self,
        emotion,
        confidence,
        pitch,
        yaw,
        roll
    ):

        self.total_frames += 1

        # -----------------------------
        # Emotion
        # -----------------------------

        if emotion is not None:

            self.emotions.append(emotion)

        # -----------------------------
        # Confidence
        # -----------------------------

        if confidence is not None:

            self.confidences.append(confidence)

        # -----------------------------
        # Head Pose
        # -----------------------------

        if pitch is not None:

            self.pitch_values.append(pitch)

        if yaw is not None:

            self.yaw_values.append(yaw)

        if roll is not None:

            self.roll_values.append(roll)

        # -----------------------------
        # Eye Contact
        # -----------------------------

        if yaw is not None:

            if -15 <= yaw <= 15:

                self.eye_contact_frames += 1

    # -----------------------------------------
    # Average Helper
    # -----------------------------------------

    def average(self, values):

        if len(values) == 0:

            return 0

        return round(sum(values) / len(values), 2)

    # -----------------------------------------
    # Emotion Percentage
    # -----------------------------------------

    def emotion_percentages(self):

        if len(self.emotions) == 0:

            return {}

        counter = Counter(self.emotions)

        result = {}

        total = len(self.emotions)

        for emotion, count in counter.items():

            result[emotion] = round(
                (count / total) * 100,
                2
            )

        return result

    # -----------------------------------------
    # Dominant Emotion
    # -----------------------------------------

    def dominant_emotion(self):

        if len(self.emotions) == 0:

            return "Unknown"

        counter = Counter(self.emotions)

        return counter.most_common(1)[0][0]

    # -----------------------------------------
    # Eye Contact Percentage
    # -----------------------------------------

    def eye_contact_percentage(self):

        if self.total_frames == 0:

            return 0

        return round(

            (self.eye_contact_frames /
             self.total_frames) * 100,

            2

        )

    # -----------------------------------------
    # Final Summary
    # -----------------------------------------

    def generate_summary(self):

        summary = {

            "total_frames":

                self.total_frames,

            "dominant_emotion":

                self.dominant_emotion(),

            "emotion_percentages":

                self.emotion_percentages(),

            "average_confidence":

                self.average(
                    self.confidences
                ),

            "average_pitch":

                self.average(
                    self.pitch_values
                ),

            "average_yaw":

                self.average(
                    self.yaw_values
                ),

            "average_roll":

                self.average(
                    self.roll_values
                ),

            "eye_contact_percentage":

                self.eye_contact_percentage()

        }

        return summary
if __name__ == "__main__":

    summary = AnswerSummary()

    summary.add_frame("happy", 95, 2, 5, 1)
    summary.add_frame("happy", 90, 3, 10, 0)
    summary.add_frame("neutral", 80, -1, 20, 2)

    print(summary.generate_summary())