import os
import shutil
from fastapi import APIRouter,UploadFile,File,Depends,HTTPException
from app.core.dependencies import get_current_user
from app.models.user import User
from app.utils.document_processor import extract_text_from_pdf,extract_text_from_docx
from app.utils.text_chunker import chunk_text
from app.vector_db.chromadb_client import collection,embedding_model
from app.tasks.document_tasks import process_document_task
from app.uploads.service import get_user_uploads

router = APIRouter(
    prefix="/api/uploads",
    tags=["Uploads"]
)


ALLOWED_EXTENSIONS = [
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".docx"
]


@router.get("/")
def list_uploaded_files(
    current_user: User = Depends(get_current_user)
):

    return {
        "files": get_user_uploads(
            current_user.id
        )
    }


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    print("file uploaded", file)

    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="File type not allowed"
        )

    upload_path = f"uploads/{file.filename}"

    # SAVE FILE
    with open(upload_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # CLOSE FILE STREAM
    file.file.close()

    if file_extension in [".pdf", ".docx"]:
        process_document_task.delay(
        upload_path,
        file_extension,
        file.filename,
        current_user.id
    )

    return {
        "message": "File uploaded successfully",
        "filename": file.filename
    }
