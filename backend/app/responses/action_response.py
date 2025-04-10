from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ActionResponse(BaseModel):
    status: str
    code: str
    messages: Optional[List[Dict[str, Any]]] = None


def convert_to_action_response(state: Dict) -> ActionResponse:

    return ActionResponse(
        status= "code_generated",
        code= state.get("generated_code"),
        messages= state.get("messages", [])
    )