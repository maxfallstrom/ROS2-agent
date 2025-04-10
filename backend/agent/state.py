from typing_extensions import TypedDict
from typing import List, Optional, Dict, Any

class AgentState(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    parsed_prompt: Optional[Dict[str, Any]]
    task_description: Optional[str]
    terrain_type: Optional[str]
    payload_kg: Optional[float]
    robot_type: Optional[str]
    robot_matches: Optional[List[Dict[str, Any]]]
    selected_robot: Optional[Dict[str, Any]]
    action_command: Optional[str]
    missing_fields: Optional[List[str]]
    error: Optional[str]