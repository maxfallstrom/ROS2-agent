from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PromptResponse(BaseModel):
    status: str
    messages: List[Dict[str, Any]]
    robot_matches: Optional[List[Dict[str, Any]]] = None
    missing_fields: Optional[List[str]] = None


def convert_to_dto(state: Dict) -> PromptResponse:
    return PromptResponse(
        status="complete",
        messages=state.get("messages", []),
        robot_matches=state.get("robot_matches"),
        missing_fields=state.get("missing_fields")
    )