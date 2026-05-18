from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db,get_current_user
from app.models.note import Note
from app.models.user import User
from app.ai.service import generate_summary
from app.ai.schemas import (
    AskQuestionSchema,
    AskUploadedFileSchema,
    UploadedFileSummarySchema
)
from app.ai.service import ask_notes_ai
from app.ai.service import retrieve_relevant_notes
from fastapi.responses import StreamingResponse
from app.ai.service import stream_ai_response
from app.ai.service import hybrid_retrieval
from app.ai.service import get_chat_history,conversational_ai_response
from app.models.chat import ChatMessage
from app.uploads.service import (
    build_upload_context,
    get_upload_chunks
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/summarize/{note_id}")
def summarize_note(
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

    summary = generate_summary(
        note.content
    )

    return {
        "note_title": note.title,
        "summary": summary
    }


@router.post("/uploads/summarize")
def summarize_uploaded_file(
    data: UploadedFileSummarySchema,
    current_user: User = Depends(get_current_user)
):

    chunks = get_upload_chunks(
        data.filename,
        current_user.id
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found or not processed yet"
        )

    summary = generate_summary(
        build_upload_context(chunks)
    )

    return {
        "filename": data.filename,
        "summary": summary
    }


@router.post("/uploads/ask")
def ask_ai_about_uploaded_file(
    data: AskUploadedFileSchema,
    current_user: User = Depends(get_current_user)
):

    chunks = get_upload_chunks(
        data.filename,
        current_user.id
    )

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="Uploaded file not found or not processed yet"
        )

    answer = ask_notes_ai(
        data.question,
        build_upload_context(chunks)
    )

    return {
        "filename": data.filename,
        "question": data.question,
        "answer": answer,
        "sources": [
            {
                "source": chunk["source"],
                "title": chunk["title"]
            }
            for chunk in chunks
        ]
    }
    
@router.post("/ask")
def ask_ai_about_notes(

    data: AskQuestionSchema,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    relevant_notes = hybrid_retrieval(

        db,

        data.question,

        current_user.id
    )

    if not relevant_notes:

        raise HTTPException(
            status_code=404,
            detail="No relevant notes found"
        )

    notes_context = ""

    for chunk in relevant_notes:

        notes_context += (

            f"Source: {chunk['source']}\n"

            f"Content: {chunk['content']}\n\n"
        )

    # SAVE USER MESSAGE
    user_message = ChatMessage(

        role="user",

        content=data.question,

        user_id=current_user.id
    )

    db.add(user_message)

    db.commit()

    # GET CHAT HISTORY
    history = get_chat_history(

        db,

        current_user.id
    )

    # GENERATE AI RESPONSE
    answer = conversational_ai_response(

        data.question,

        notes_context,

        history
    )

    # SAVE AI RESPONSE
    assistant_message = ChatMessage(

        role="assistant",

        content=answer,

        user_id=current_user.id
    )

    db.add(assistant_message)

    db.commit()

    return {

        "question": data.question,

        "answer": answer,

        "sources": [

            {
                "source": chunk["source"],
                "title": chunk["title"]
            }

            for chunk in relevant_notes
        ]
    }
    
@router.post("/ask-stream")
def ask_ai_stream(

    data: AskQuestionSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    relevant_notes = hybrid_retrieval(db,data.question,current_user.id)

    notes_context = ""

    for chunk in relevant_notes:
        notes_context += (
        f"Source: {chunk['source']}\n"
        f"Content: {chunk['content']}\n\n")

    response_stream = stream_ai_response(

        data.question,

        notes_context
    )

    return StreamingResponse(
        response_stream,
        media_type="text/plain"
    )
