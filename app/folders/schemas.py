from pydantic import BaseModel


class FolderCreateSchema(BaseModel):
    name: str


class FolderUpdateSchema(BaseModel):
    name: str