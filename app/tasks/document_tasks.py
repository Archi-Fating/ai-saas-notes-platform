import os

from app.celery_worker import celery

from app.utils.document_processor import (
    extract_text_from_pdf,
    extract_text_from_docx
)

from app.utils.text_chunker import (
    chunk_text
)

from app.vector_db.chromadb_client import (
    collection,
    embedding_model
)


@celery.task
def process_document_task(
    file_path: str,
    file_extension: str,
    filename: str,
    user_id: int
):

    extracted_text = ""

    if file_extension == ".pdf":

        extracted_text = extract_text_from_pdf(
            file_path
        )

    elif file_extension == ".docx":

        extracted_text = extract_text_from_docx(
            file_path
        )

    if extracted_text:

        chunks = chunk_text(
            extracted_text
        )

        for index, chunk in enumerate(chunks):

            embedding = embedding_model.encode(
                chunk
            ).tolist()

            collection.upsert(

                ids=[
                    f"upload_{user_id}_{filename}_{index}"
                ],

                embeddings=[
                    embedding
                ],

                documents=[
                    chunk
                ],

                metadatas=[
                    {
                        "user_id": user_id,
                        "source": filename,
                        "title": filename,
                        "type": "upload"
                    }
                ]
            )

    return "Document processed"
