from typing_extensions import TypedDict
from typing import List, Optional, Dict, Any

class AgentState(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    status: Optional[str]
    robot_matches: Optional[List[Dict[str, Any]]]
    error: Optional[str]