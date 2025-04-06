import os
import json
from typing import Optional, Dict
from uuid import UUID

# Temporary in-memory store, replace with Supabase later
STATE_STORE: Dict[str, Dict] = {}


def load_state(session_id: UUID) -> Dict:
    """Load agent state for a given user ID."""
    return STATE_STORE.get(session_id, {})


def save_state(session_id: UUID, state: Dict) -> None:
    """Save agent state for a given user ID."""
    STATE_STORE[session_id] = state


def clear_state(session_id: UUID) -> None:
    """Reset agent state for a user."""
    if session_id in STATE_STORE:
        del STATE_STORE[session_id]
