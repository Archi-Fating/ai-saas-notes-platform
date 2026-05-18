from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.notes.routes import router as notes_router
from app.folders.routes import router as folders_router
from app.uploads.routes import router as uploads_router
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.ai.routes import router as ai_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(notes_router)
app.include_router(folders_router)
app.include_router(uploads_router)
app.include_router(ai_router)

@app.get("/")
def home():
    index_file = FRONTEND_DIR / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return{"message":"hello app"}
