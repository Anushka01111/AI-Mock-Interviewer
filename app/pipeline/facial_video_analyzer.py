"""
facial_video_analyzer.py
--------------------------
Adapts Member 4's live-webcam pipeline (interview_camera.py) to process
an uploaded video file instead of a live camera feed. Samples frames at
a fixed rate, runs face crop -> emotion detection -> head pose per frame,
and returns the same AnswerSummary structure as the original live version.
"""

import cv2

from app.pipeline.face_crop import crop_face
from app.pipeline.emotion_detector import predict_emotion
from app.pipeline.head_pose_utils import get_head_pose
from app.pipeline.interview_analyzer import analyze_interview
from app.pipeline.answer_summary import AnswerSummary

from PIL import Image


def analyze_video_file(video_path: str, sample_fps: float = 5.0) -> dict:
    """
    Process an uploaded video file frame-by-frame (sampled at sample_fps)
    and return the same summary structure Member 4's live pipeline produces.

    Returns a dict with 'last_frame' (final frame analysis) and
    'answer_summary' (aggregated stats across all sampled frames) —
    identical shape to interview_output.json.
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, int(video_fps / sample_fps))

    summary = AnswerSummary()
    last_result = None
    frame_index = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Only process every Nth frame to hit our target sample rate
        if frame_index % frame_interval == 0:
            face, bbox = crop_face(frame)

            if face is not None:
                rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb)

                emotion, confidence, scores = predict_emotion(pil_image)
                pitch, yaw, roll = get_head_pose(frame)

                result = analyze_interview(emotion, confidence, pitch, yaw, roll)
                last_result = result

                summary.add_frame(emotion, confidence, pitch, yaw, roll)

        frame_index += 1

    cap.release()

    interview_summary = summary.generate_summary()

    return {
        "last_frame": last_result,
        "answer_summary": interview_summary
    }


def get_facial_score(video_path: str, sample_fps: float = 5.0) -> float:
    """
    Convenience wrapper — returns a single 0.0-1.0 facial score suitable
    for the Score.facial_score column, derived from the last frame's
    'score' field (0-100 scale from analyze_interview).

    If no face was detected in any sampled frame, returns 0.0.
    """
    result = analyze_video_file(video_path, sample_fps=sample_fps)

    last_frame = result.get("last_frame")
    if not last_frame:
        return 0.0

    raw_score = last_frame.get("score", 0)  # 0-100 scale
    return round(raw_score / 100.0, 3)