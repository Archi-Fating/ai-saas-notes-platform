from pydantic import BaseModel


class NoteCreateSchema(BaseModel):
    title: str
    content: str


class NoteUpdateSchema(BaseModel):
    title: str
    content: str