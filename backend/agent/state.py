from typing_extensions import TypedDict
from typing import List, Optional, Dict, Any
from uuid import UUID

class AgentState(TypedDict, total=False):
    session_id: UUID
    messages: List[Dict[str, Any]]
    status: Optional[str]
    robot_matches: Optional[List[Dict[str, Any]]]
    error: Optional[str]