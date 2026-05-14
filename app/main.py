from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.notes.routes import router as notes_router
from app.folders.routes import router as folders_router
from app.uploads.routes import router as uploads_router
from fastapi.staticfiles import StaticFiles
from app.ai.routes import router as ai_router

app=FastAPI()
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(notes_router)
app.include_router(folders_router)
app.include_router(uploads_router)
app.include_router(ai_router)


@app.get("/")
def home():
    return{"message":"hello app"}