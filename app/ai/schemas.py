from pydantic import BaseModel


class AskQuestionSchema(BaseModel):
    question: str


class UploadedFileSummarySchema(BaseModel):
    filename: str


class AskUploadedFileSchema(BaseModel):
    filename: str
    question: str
