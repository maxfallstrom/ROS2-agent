from pydantic import BaseModel
from typing import Dict
from  uuid import UUID

class ActionRequest(BaseModel):
    user_id: UUID
    session_id: UUID
    selected_robot: Dict
    action_prompt: str
