from pydantic import BaseModel
from typing import Optional, Dict
from  uuid import UUID

class PromptRequest(BaseModel):
    user_id: UUID
    session_id: UUID
    prompt: str
    metadata: Optional[Dict] = None