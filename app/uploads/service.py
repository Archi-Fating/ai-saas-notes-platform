from app.vector_db.chromadb_client import collection


def get_user_uploads(user_id: int) -> list[dict]:
    results = collection.get(
        where={
            "user_id": user_id
        },
        include=[
            "metadatas"
        ]
    )

    files = {}

    for metadata in results.get("metadatas") or []:
        is_upload = (
            metadata.get("type") == "upload"
            or (
                metadata.get("source")
                and "note_id" not in metadata
            )
        )

        if not is_upload:
            continue

        filename = metadata.get("source")

        if not filename:
            continue

        files[filename] = {
            "filename": filename,
            "title": metadata.get("title", filename)
        }

    return sorted(
        files.values(),
        key=lambda item: item["filename"].lower()
    )


def get_upload_chunks(
    filename: str,
    user_id: int
) -> list[dict]:
    results = collection.get(
        where={
            "source": filename
        },
        include=[
            "documents",
            "metadatas"
        ]
    )

    chunks = []

    for document, metadata in zip(
        results.get("documents") or [],
        results.get("metadatas") or []
    ):
        if metadata.get("user_id") != user_id:
            continue

        is_upload = (
            metadata.get("type") == "upload"
            or (
                metadata.get("source")
                and "note_id" not in metadata
            )
        )

        if not is_upload:
            continue

        chunks.append(
            {
                "content": document,
                "source": metadata.get("source", filename),
                "title": metadata.get("title", filename)
            }
        )

    return chunks


def build_upload_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        (
            f"Source: {chunk['source']}\n"
            f"Content: {chunk['content']}"
        )
        for chunk in chunks
    )
