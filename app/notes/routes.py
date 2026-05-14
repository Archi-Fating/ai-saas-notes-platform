from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.notes.schemas import NoteCreateSchema,NoteUpdateSchema
from app.models.note import Note
from app.models.user import User
from app.core.dependencies import get_db,get_current_user
from fastapi import Query
from app.models.folder import Folder
from app.vector_db.chromadb_client import collection,embedding_model
from app.utils.text_chunker import chunk_text

router=APIRouter(prefix="/notes",tags=["Notes"])


#CREATE NOTE API
@router.post("/")
def create_note(
    note: NoteCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_note = Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    
    
    chunks = chunk_text(
    note.content
)

    for index, chunk in enumerate(chunks):

        embedding = embedding_model.encode(chunk).tolist()

        collection.add(
            ids=[f"{new_note.id}_{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[
            {
                "user_id": current_user.id,
                "title": note.title,
                "note_id": new_note.id
            }
        ]
    )

    return {
        "message": "Note created successfully",
        "note": {
            "id": new_note.id,
            "title": new_note.title,
            "content": new_note.content
        }
    }
    
#GET ALL NOTES
@router.get("/")
def get_notes(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=100),
    search: str = "",
    sort: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Note).filter(
        Note.user_id == current_user.id
    )

    if search:
        query = query.filter(
            Note.title.ilike(f"%{search}%")
        )

    if sort == "desc":
        query = query.order_by(Note.id.desc())

    else:
        query = query.order_by(Note.id.asc())
    skip = (page - 1) * limit
    notes = query.offset(skip).limit(limit).all()

    return {
        "page": page,
        "limit": limit,
        "total": len(notes),
        "notes": notes
    }

#GET SINGLE NOTE
@router.get("/{note_id}")
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note

#update notes
@router.put("/{note_id}")
def update_note(
    note_id: int,
    updated_note: NoteUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    note.title = updated_note.title
    note.content = updated_note.content

    db.commit()
    db.refresh(note)

    return {
        "message": "Note updated successfully",
        "note": note
    }
    
#delete notes   
@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted successfully"
    }
    
@router.put("/{note_id}/move/{folder_id}")
def move_note_to_folder(
    note_id: int,
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()

    if not folder:
        raise HTTPException(
            status_code=404,
            detail="Folder not found"
        )

    note.folder_id = folder.id

    db.commit()
    db.refresh(note)

    return {
        "message": "Note moved successfully",
        "note_id": note.id,
        "folder_id": folder.id
    }
    
