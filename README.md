# AI Mock Interviewer

An AI-powered mock interview system that parses resumes, generates personalised interview questions, and evaluates candidate answers across three dimensions: answer accuracy (NLP), speech confidence (audio analysis), and facial engagement (computer vision).

## Features
- Resume parsing (PDF -> structured data)
- LLM-generated interview questions with difficulty scaling (OpenAI GPT-4o)
- Speech-to-text transcription (Whisper) with prosody/confidence scoring
- Facial emotion detection and head pose analysis (MediaPipe + HuggingFace)
- Semantic answer scoring (Sentence-BERT)
- Automated feedback report generation with PDF export

## Tech Stack
FastAPI, MySQL, SQLAlchemy, Redis, OpenAI API, Whisper, Librosa, MediaPipe, HuggingFace Transformers, Sentence-Transformers

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements-full.txt`
5. Copy `.env.example` to `.env` and fill in your own values
6. Set up MySQL database and run: `python -m app.database.init_db`
7. Download the face landmarker model:

curl -o app/pipeline/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task

8. Run the server: `python -m uvicorn app.main:app --reload`
9. Visit `http://127.0.0.1:8000/docs` for the interactive API docs

## Notes
- On Windows, if you hit DLL loading errors (spaCy, matplotlib, llvmlite), check Windows Security > App & browser control > Smart App Control settings.