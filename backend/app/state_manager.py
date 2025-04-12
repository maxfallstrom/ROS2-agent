from supabase import create_client
from uuid import UUID
from typing import Dict, Any
from agent.helpers.api_keys import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_state(session_id: UUID) -> Dict[str, Any]:
    response = supabase.table("state").select("*").eq("session_id", str(session_id)).limit(1).execute()
    if response.data and len(response.data) > 0:
        return response.data[0]
    return {}

def save_state(session_id: UUID, state: Dict[str, Any]) -> None:
    state["session_id"] = str(session_id)
    supabase.table("state").upsert(state, on_conflict="session_id").execute()
