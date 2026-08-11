# AI Mock Interviewer — Full Setup Guide

An AI-powered mock interview platform. Upload a resume, get personalised interview questions, answer them via webcam + mic, and receive a scored feedback report across three dimensions: answer accuracy (NLP), speech confidence (audio), and body language (computer vision).

**Single repo, two parts:**
- `backend/` — FastAPI + Python ML pipeline
- `frontend/` — React app

Repo: https://github.com/Anushka01111/AI-Mock-Interviewer

---

## Prerequisites

Install these first, in order:

1. **Python 3.11** — https://www.python.org/downloads/ (check "Add to PATH" during install)
2. **Node.js LTS** — https://nodejs.org
3. **MySQL 8.0** — https://dev.mysql.com/downloads/installer/ (choose "Server only")
4. **Memurai** (Redis for Windows) — https://www.memurai.com/get-memurai (free Developer edition)
5. **Git** — https://git-scm.com/downloads

On Windows, if you hit `DLL load failed` errors for spaCy, matplotlib, or llvmlite during setup:
Go to **Windows Security → App & browser control → Smart App Control** and turn it **Off**. This blocks unsigned compiled libraries by default.

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/Anushka01111/AI-Mock-Interviewer.git
cd AI-Mock-Interviewer
```

You'll see two folders: `backend/` and `frontend/`.

---

## Step 2 — Backend setup

```bash
cd backend
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements-full.txt
```

This installs the full ML stack (torch, tensorflow, mediapipe, whisper, etc.) — takes several minutes.

### Download the face landmark model (not included in git — 3.75MB)
```bash
curl -o app\pipeline\face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

### Set up MySQL
```bash
mysql -u root -p
```
```sql
CREATE DATABASE ai_interview_db;
CREATE USER 'aiuser'@'localhost' IDENTIFIED BY 'YourPasswordHere';
GRANT ALL PRIVILEGES ON ai_interview_db.* TO 'aiuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```
**Important:** avoid special characters like `@` in the password — they break the database connection URL. Use a simple alphanumeric password.

### Create your `.env` file
```bash
copy .env.example .env
```
Edit `.env` and fill in:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_interview_db
DB_USER=aiuser
DB_PASSWORD=YourPasswordHere
DATABASE_URL=mysql+pymysql://aiuser:YourPasswordHere@localhost/ai_interview_db
REDIS_HOST=localhost
REDIS_PORT=6379
OPENAI_API_KEY=your_openai_api_key_here
```
Get an OpenAI key at https://platform.openai.com/api-keys

### Initialize the database tables
```bash
python -m app.database.init_db
```
Should print `Tables created successfully`.

### Start the backend
```bash
python -m uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` to confirm it's running — you should see the Swagger API docs.

---

## Step 3 — Frontend setup

Open a **new terminal** (keep the backend running in the first one):

```bash
cd AI-Mock-Interviewer\frontend
npm install
npm run dev
```

It will print a URL like `http://localhost:5173/`. Open that in your browser.

---

## Step 4 — Use the app

1. Go to the frontend URL, click "Create one" to register an account
2. Log in
3. Upload a resume PDF — the app generates 10 personalised interview questions
4. Click "Begin interview" — allow camera and microphone access when prompted
5. Answer each question by recording, then submit
6. After the last question, view your scored feedback report and download the PDF

---

## Common Issues

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on backend startup | `pip install <missing-package-name>` inside the activated venv |
| `DLL load failed` (spaCy/matplotlib/llvmlite) | Turn off Windows Smart App Control (see Prerequisites) |
| CORS errors in browser console | Backend already allows all localhost ports via regex in `main.py` — restart backend if you still see this |
| "Invalid or expired token" in the app | Log out and log back in — tokens expire after a set time |
| MySQL `Access denied` errors | Check your password has no special characters like `@` breaking the connection URL |
| Whisper transcription fails with `WinError 2` | Backend bundles its own ffmpeg via `imageio-ffmpeg` — should work automatically; if not, ensure `pip install imageio-ffmpeg` succeeded |

---

## Tech Stack

**Backend:** FastAPI, MySQL, SQLAlchemy, Redis, JWT auth
**AI/ML:** OpenAI GPT-4o-mini (questions + feedback), Whisper (speech-to-text), Librosa (prosody analysis), XGBoost (speech confidence), MediaPipe (head pose), HuggingFace Transformers (facial emotion), Sentence-BERT (answer scoring)
**Frontend:** React, Vite, Tailwind CSS, React Router, Axios
**Reporting:** ReportLab (PDF generation), Matplotlib (charts)

---

## Architecture

```
Resume PDF upload
    -> Text extraction + parsing
    -> GPT-4o-mini generates 10 personalised questions + ideal answers
    -> Candidate records answer (audio + video, browser MediaRecorder API)
    -> Whisper transcribes audio -> Librosa extracts prosody -> confidence score
    -> MediaPipe + HuggingFace analyse video frames -> facial/eye-contact score
    -> Sentence-BERT compares transcript to ideal answer -> accuracy score
    -> All scores aggregated across the session
    -> GPT-4o-mini synthesises narrative feedback
    -> Report displayed in-app + downloadable as PDF
```
