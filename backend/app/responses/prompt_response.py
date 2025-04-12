from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PromptResponse(BaseModel):
    messages: List[Dict[str, Any]]
    robot_matches: Optional[List[Dict[str, Any]]] = None


def convert_stream_chunk(state: dict) -> dict:
    return {
        "messages": state.get("messages", []),
        "robot_matches": state.get("robot_matches", [])
    }
