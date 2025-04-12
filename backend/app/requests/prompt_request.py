from pydantic import BaseModel
from typing import Optional, Dict
from  uuid import UUID

class PromptRequest(BaseModel):
    session_id: UUID
    prompt: str