from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    title: str = Field(default="User Document")
    text: str
class AskRequest(BaseModel):
    question: str
