import chromadb
from sentence_transformers import SentenceTransformer



client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="notes"
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)