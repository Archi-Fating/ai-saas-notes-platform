from pydantic import BaseModel


class AskQuestionSchema(BaseModel):
    question: str