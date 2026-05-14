from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db,get_current_user
from app.models.folder import Folder
from app.models.user import User
from app.folders.schemas import FolderCreateSchema,FolderUpdateSchema
from app.models.note import Note

router = APIRouter(
    prefix="/folders",
    tags=["Folders"]
)

@router.post("/")
def create_folder(
    folder: FolderCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_folder = Folder(
        name=folder.name,
        user_id=current_user.id
    )

    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    return {
        "message": "Folder created successfully",
        "folder": new_folder
    }


#   
@router.get("/")
def get_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    folders = db.query(Folder).filter(
        Folder.user_id == current_user.id
    ).all()
    
    return folders

#GET NOTES INSIDE FOLDER
@router.get("/{folder_id}/notes")
def get_notes_in_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()

    if not folder:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    notes = db.query(Note).filter(
        Note.folder_id == folder.id,
        Note.user_id == current_user.id
    ).all()

    return {
        "folder": folder.name,
        "notes": notes
    }