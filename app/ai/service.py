from groq import Groq
from app.models.note import Note
from app.config import GROQ_API_KEY
from app.vector_db.chromadb_client import collection,embedding_model
from app.models.chat import ChatMessage


client = Groq(
    api_key=GROQ_API_KEY
)


def generate_summary(note_content: str):

    response = client.chat.completions.create(

        model="qwen/qwen3-32b",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant "
                    "that summarizes notes clearly."
                )
            },

            {
                "role": "user",
                "content": (
                    f"Summarize this note:\n\n"
                    f"{note_content}"
                )
            }

        ]

    )

    return response.choices[0].message.content


def ask_notes_ai(
    question: str,
    notes_context: str
):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are an AI assistant "
                    "that answers questions "
                    "ONLY using the provided notes."
                )
            },

            {
                "role": "user",
                "content": (
                    f"NOTES:\n\n"
                    f"{notes_context}\n\n"
                    f"QUESTION:\n{question}"
                )
            }

        ]

    )

    return response.choices[0].message.content

def retrieve_relevant_notes(
    question: str,
    user_id: int
):

    question_embedding = embedding_model.encode(question).tolist()

    results = collection.query(

    query_embeddings=[question_embedding],
    n_results=5,
    where={
        "user_id": user_id
    }
)


    documents = results["documents"][0]

    metadatas = results["metadatas"][0]

    retrieved_chunks = []

    for doc, metadata in zip(
    documents,
    metadatas):
        retrieved_chunks.append(
            {
                "content": doc,
                "source": metadata.get(
                    "source",
                    "note"
                ),
                "title": metadata.get(
                    "title",
                    "Untitled"
                )
            }
        )

    return retrieved_chunks


def stream_ai_response(
    question: str,
    notes_context: str
):

    stream = client.chat.completions.create(

        model="qwen/qwen3-32b",

        messages=[

            {
                "role": "system",
                "content": (
                    "You are an AI assistant "
                    "that answers questions "
                    "using provided notes."
                )
            },

            {
                "role": "user",
                "content": (
                    f"NOTES:\n\n"
                    f"{notes_context}\n\n"
                    f"QUESTION:\n{question}"
                )
            }

        ],

        stream=True
    )

    for chunk in stream:

        content = (
            chunk.choices[0]
            .delta.content
        )

        if content:

            yield content
            

def keyword_search_notes(
    db,
    question: str,
    user_id: int
):

    notes = db.query(Note).filter(
        Note.user_id == user_id
    ).all()

    matched_notes = []

    question_words = question.lower().split()

    for note in notes:

        note_text = (
            note.title + " " + note.content
        ).lower()

        for word in question_words:

            if word in note_text:

                matched_notes.append(
                    {
                        "content": note.content,
                        "source": "database_note",
                        "title": note.title
                    }
                )

                break

    return matched_notes

def hybrid_retrieval(
    db,
    question: str,
    user_id: int
):

    semantic_results = retrieve_relevant_notes(
        question,
        user_id
    )

    keyword_results = keyword_search_notes(
        db,
        question,
        user_id
    )

    combined_results = []

    seen_content = set()

    for result in (
        semantic_results + keyword_results
    ):

        content = result["content"]

        if content not in seen_content:

            combined_results.append(
                result
            )

            seen_content.add(content)

    return combined_results[:5]

def get_chat_history(
    db,
    user_id: int,
    limit: int = 10
):

    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == user_id
    ).order_by(
        ChatMessage.id.desc()
    ).limit(limit).all()

    messages.reverse()

    history = []

    for msg in messages:

        history.append(
            {
                "role": msg.role,
                "content": msg.content
            }
        )

    return history

def conversational_ai_response(

    question: str,

    notes_context: str,

    history: list
):

    messages = [

        {
            "role": "system",
            "content": (
                "You are an AI assistant "
                "that answers using "
                "retrieved notes."
            )
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": (
                f"NOTES:\n\n"
                f"{notes_context}\n\n"
                f"QUESTION:\n{question}"
            )
        }
    )

    response = client.chat.completions.create(

        model="qwen/qwen3-32b",

        messages=messages
    )

    return response.choices[0].message.content