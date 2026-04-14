from typing import Optional
from pydantic import BaseModel, field_validator


class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("message não pode ser vazio")
        return v


class Source(BaseModel):
    section: str


class MessageResponse(BaseModel):
    answer: str
    sources: list[Source]
