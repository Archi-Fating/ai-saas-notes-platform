# AI SaaS Notes Platform

AI SaaS Notes Platform is a FastAPI-based notes application that combines personal note management with AI-powered search, summarization, document upload processing, and conversational question answering. It is designed as a backend-first SaaS project with JWT authentication, PostgreSQL persistence, vector search through ChromaDB, asynchronous document processing with Celery, and a lightweight frontend served from the FastAPI app.

The platform lets users create notes, organize them into folders, upload supported files, summarize note or document content, and ask questions against their own saved knowledge base. Notes and processed documents are chunked, embedded with Sentence Transformers, and stored in ChromaDB so AI responses can be grounded in relevant user-owned content.

## Core Features

- User registration and login with JWT bearer tokens.
- Password hashing with Passlib and bcrypt.
- Authenticated note CRUD operations.
- Search, pagination, and sort support for note lists.
- Folder creation and note organization.
- File upload support for PDF, DOCX, PNG, JPG, and JPEG files.
- Background processing for PDF and DOCX uploads with Celery.
- Text extraction, chunking, embedding, and vector storage.
- AI note summarization through Groq models.
- AI question answering over notes with hybrid semantic and keyword retrieval.
- Streaming AI answer endpoint.
- Conversational chat history for note Q&A.
- Static frontend served from `frontend/index.html`.
- Docker Compose setup for API, PostgreSQL, Redis, and Celery.

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT, python-jose, Passlib, bcrypt |
| AI Provider | Groq |
| Embeddings | Sentence Transformers, `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB |
| Background Jobs | Celery |
| Broker / Backend | Redis |
| Document Parsing | pypdf, python-docx/lxml dependencies |
| Frontend | Static HTML, CSS, JavaScript |
| Deployment | Docker, Docker Compose |

## Project Structure

```text
.
|-- app/
|   |-- ai/                 # AI summarize, ask, stream, retrieval services
|   |-- auth/               # Register, login, token creation
|   |-- core/               # Security and dependency helpers
|   |-- folders/            # Folder APIs and schemas
|   |-- models/             # SQLAlchemy models
|   |-- notes/              # Note APIs, schemas, and service layer
|   |-- tasks/              # Celery document processing tasks
|   |-- uploads/            # Upload APIs and upload lookup services
|   |-- utils/              # Text extraction and chunking utilities
|   |-- vector_db/          # ChromaDB client and embedding model
|   |-- celery_worker.py    # Celery app configuration
|   |-- config.py           # Environment-based app settings
|   |-- database.py         # SQLAlchemy engine and session setup
|   `-- main.py             # FastAPI app entry point
|-- alembic/                # Database migrations
|-- frontend/               # Browser UI served by FastAPI
|-- uploads/                # Uploaded user files
|-- chroma_db/              # Persistent ChromaDB vector database
|-- docker-compose.yml
|-- Dockerfile
|-- requirements.txt
`-- README.md
```

## How It Works

### Note Flow

```text
User creates a note
    -> FastAPI validates the request
    -> Note is saved in PostgreSQL
    -> Note content is split into chunks
    -> Chunks are converted into embeddings
    -> Embeddings and metadata are stored in ChromaDB
    -> API returns the created note
```

### AI Question Flow

```text
User asks a question
    -> Question is embedded
    -> ChromaDB returns semantically relevant note chunks
    -> Keyword search adds direct text matches
    -> Duplicate results are removed
    -> Relevant context is sent to Groq
    -> Answer and sources are returned to the user
```

### Upload Flow

```text
User uploads a file
    -> FastAPI validates the file extension
    -> File is saved in the uploads directory
    -> PDF/DOCX files are queued for Celery processing
    -> Celery extracts document text
    -> Text is chunked and embedded
    -> Document chunks are stored in ChromaDB
    -> User can summarize or ask questions about the file
```

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:archi123@localhost:5432/ai_notes
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GROQ_API_KEY=your-groq-api-key
REDIS_URL=redis://localhost:6379/0
```

When running with Docker Compose, the API container uses the internal PostgreSQL hostname from `docker-compose.yml`:

```env
DATABASE_URL=postgresql://postgres:archi123@postgres:5432/ai_notes
REDIS_URL=redis://redis:6379/0
```

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Configure your `.env` file.

4. Run database migrations.

```bash
alembic upgrade head
```

5. Start the FastAPI app.

```bash
uvicorn app.main:app --reload
```

6. Open the app.

```text
http://127.0.0.1:8000
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Running Background Workers

Redis must be running before starting Celery. For local development, start Redis and then run:

```bash
celery -A app.celery_worker.celery worker --pool=solo --loglevel=info
```

The `--pool=solo` option is useful on Windows development machines.

## Docker Setup

Start the full stack:

```bash
docker compose up --build
```

This starts:

- FastAPI API on port `8000`.
- PostgreSQL on port `5432`.
- Redis on port `6379`.
- Celery worker for background document processing.

After the containers are running, apply migrations inside the API container if needed:

```bash
docker compose exec api alembic upgrade head
```

## Main API Endpoints

### Auth

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create a new user account |
| POST | `/auth/login` | Login and receive a JWT token |

### Notes

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/notes/` | Create a note |
| GET | `/notes/` | List notes with pagination, search, and sort |
| GET | `/notes/{note_id}` | Get one note |
| PUT | `/notes/{note_id}` | Update a note |
| DELETE | `/notes/{note_id}` | Delete a note |
| PUT | `/notes/{note_id}/move/{folder_id}` | Move a note into a folder |

### Folders

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/folders/` | Create a folder |
| GET | `/folders/` | List user folders |
| GET | `/folders/{folder_id}/notes` | List notes inside a folder |

### Uploads

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/uploads/` | Upload a supported file |
| GET | `/api/uploads/` | List uploaded files for the current user |

### AI

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/ai/summarize/{note_id}` | Summarize a note |
| POST | `/ai/ask` | Ask a question about notes |
| POST | `/ai/ask-stream` | Stream an AI answer about notes |
| POST | `/ai/uploads/summarize` | Summarize an uploaded processed file |
| POST | `/ai/uploads/ask` | Ask a question about an uploaded processed file |

Most application endpoints require an `Authorization: Bearer <token>` header after login.

## Database Migrations

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe your change"
```

Apply migrations:

```bash
alembic upgrade head
```

## Supported Upload Types

- `.pdf`
- `.docx`
- `.png`
- `.jpg`
- `.jpeg`

PDF and DOCX files are processed for AI search and Q&A. Image files are stored as uploads, but they are not currently converted into searchable text.

## Notes for Development

- `uploads/` stores uploaded files.
- `chroma_db/` stores the persistent vector database.
- `app/vector_db/chromadb_client.py` loads the Sentence Transformer embedding model.
- `app/tasks/document_tasks.py` handles asynchronous document extraction and vector indexing.
- `app/ai/service.py` contains summarization, retrieval, chat history, and Groq response logic.
- `frontend/index.html` is served from `/` and `/frontend`.

## Current Status

This project is a functional AI notes platform foundation. It includes authentication, database-backed note organization, vector indexing, AI summarization, AI Q&A, upload handling, and background document processing. It can be extended with billing, team workspaces, richer frontend views, production storage for uploaded files, rate limiting, and deployment-specific configuration.
