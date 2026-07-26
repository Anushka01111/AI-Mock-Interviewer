"""
face_crop.py

Detects the largest face in an OpenCV frame
and returns only the cropped face.
"""

import cv2

# Load Haar Cascade
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def crop_face(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None, None

    # Largest face
    largest = max(faces, key=lambda r: r[2] * r[3])

    x, y, w, h = largest

    face = frame[y:y+h, x:x+w]

    return face, (x, y, w, h)