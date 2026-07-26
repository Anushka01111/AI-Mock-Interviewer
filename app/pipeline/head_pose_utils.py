"""
head_pose_utils.py

Utility functions for Head Pose Estimation.

Returns:
    pitch
    yaw
    roll

Uses:
    MediaPipe FaceLandmarker (Tasks API)
    OpenCV solvePnP()

Note: rewritten to use mediapipe's newer Tasks API (FaceLandmarker)
instead of the deprecated mp.solutions.face_mesh, since mediapipe 0.10.x+
no longer ships the classic Solutions API. Function signature and return
values are unchanged from the original — get_head_pose(frame) still
returns (pitch, yaw, roll) or (None, None, None) if no face is detected.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision


# ---------------------------------------
# Initialize MediaPipe FaceLandmarker
# ---------------------------------------

_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")

_base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
_options = mp_vision.FaceLandmarkerOptions(
    base_options=_base_options,
    running_mode=mp_vision.RunningMode.IMAGE,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)

_landmarker = mp_vision.FaceLandmarker.create_from_options(_options)


# ---------------------------------------
# Landmark IDs (same indices as before —
# FaceLandmarker uses the same 468-point
# face mesh topology as the old Solutions API)
# ---------------------------------------

LANDMARK_IDS = [
    33,     # Left eye outer corner
    263,    # Right eye outer corner
    1,      # Nose tip
    61,     # Left mouth
    291,    # Right mouth
    199     # Chin
]


# ---------------------------------------
# 3D Face Model
# ---------------------------------------

FACE_3D = np.array([

    (-30.0, 40.0, -30.0),     # Left eye
    (30.0, 40.0, -30.0),      # Right eye
    (0.0, 0.0, 0.0),          # Nose
    (-25.0, -35.0, -20.0),    # Left mouth
    (25.0, -35.0, -20.0),     # Right mouth
    (0.0, -65.0, -5.0)        # Chin

], dtype=np.float64)


def get_head_pose(frame):
    """
    Calculates Pitch, Yaw and Roll.

    Parameters
    ----------
    frame : numpy.ndarray (BGR, as returned by cv2.VideoCapture)

    Returns
    -------
    pitch, yaw, roll
    """

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = _landmarker.detect(mp_image)

    if not result.face_landmarks:
        return None, None, None

    face_landmarks = result.face_landmarks[0]

    h, w, _ = frame.shape

    face_2d = []

    for idx in LANDMARK_IDS:

        lm = face_landmarks[idx]

        x = int(lm.x * w)
        y = int(lm.y * h)

        face_2d.append((x, y))

    face_2d = np.array(face_2d, dtype=np.float64)

    focal_length = w

    cam_matrix = np.array([

        [focal_length, 0, w / 2],
        [0, focal_length, h / 2],
        [0, 0, 1]

    ], dtype=np.float64)

    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    success, rot_vec, trans_vec = cv2.solvePnP(

        FACE_3D,
        face_2d,
        cam_matrix,
        dist_matrix

    )

    if not success:
        return None, None, None
    rmat, _ = cv2.Rodrigues(rot_vec)

    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

    pitch = float(angles[0])
    yaw = float(angles[1])
    roll = float(angles[2])

    # ---------------------------------------
    # Normalize angles to [-90, 90]
    # ---------------------------------------

    def normalize(angle):

        if angle > 90:
            angle = angle - 180

        elif angle < -90:
            angle = angle + 180

        return round(angle, 2)

    pitch = normalize(pitch)
    yaw = normalize(yaw)
    roll = normalize(roll)

    return pitch, yaw, roll