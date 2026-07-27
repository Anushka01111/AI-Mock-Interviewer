from fastapi import FastAPI
from app.api.session_routes import router as session_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.session_routes import router as session_router
from app.api.question_routes import router as question_router
from app.api.answer_routes import router as answer_router
from app.api.score_routes import router as score_router
from app.api.user_routes import router as user_router

app = FastAPI(title="AI Interview System")

# Allow the React frontend (running on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(
    session_router,
    prefix="/sessions",
    tags=["Sessions"]
)

app.include_router(
    question_router,
    prefix="/questions",
    tags=["Questions"]
)

app.include_router(
    answer_router,
    prefix="/answers",
    tags=["Answers"]
)

app.include_router(
    score_router,
    prefix="/scores",
    tags=["Scores"]
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)