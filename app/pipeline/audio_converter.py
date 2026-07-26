"""
audio_converter.py
--------------------
Converts any incoming audio format (m4a, mp3, webm, etc.) to a standard
16kHz mono WAV file, which is what Member 3's audio pipeline expects.
Uses imageio-ffmpeg's bundled ffmpeg binary — no separate system install
required, works the same way on any machine (deployment-safe).
"""

import subprocess
import imageio_ffmpeg


def convert_to_wav(input_path: str, output_path: str, sample_rate: int = 16000) -> str:
    """
    Convert any audio file to a 16kHz mono WAV file using ffmpeg.
    Returns the output_path on success. Raises RuntimeError on failure.
    """
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg_exe,
        "-y",                       # overwrite output if it exists
        "-i", input_path,           # input file (any format)
        "-ar", str(sample_rate),    # resample to 16kHz
        "-ac", "1",                 # mono
        "-f", "wav",                # force WAV container
        output_path
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        stderr_text = result.stderr.decode(errors="ignore")
        raise RuntimeError(f"ffmpeg audio conversion failed: {stderr_text}")

    return output_path