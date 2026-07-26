"""
emotion_model.py
Loads the Hugging Face facial emotion detection model once
and returns the model + image processor.
Model:
dima806/facial_emotions_image_detection
"""

import time
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "dima806/facial_emotions_image_detection"


def _load_with_retry(loader_fn, max_retries: int = 3, delay_s: float = 2.0):
    """
    Try loading from HuggingFace with a few retries on transient network
    errors. Falls back to local cache automatically on the final attempt
    if the model was already downloaded before.
    """
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return loader_fn(MODEL_NAME)
        except Exception as e:
            last_error = e
            print(f"[WARNING] Model load attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(delay_s)
    # Final attempt: force local-files-only in case it's cached but the
    # network is still unreliable — this keeps deploys working offline
    # once the model has been downloaded at least once.
    print("[INFO] Retrying with local cache only...")
    try:
        return loader_fn(MODEL_NAME, local_files_only=True)
    except Exception:
        raise last_error


print("Loading Hugging Face Emotion Model...")
print("Please wait... This may take a minute the first time.")

processor = _load_with_retry(AutoImageProcessor.from_pretrained)
model = _load_with_retry(AutoModelForImageClassification.from_pretrained)

print("Emotion Model Loaded Successfully!")