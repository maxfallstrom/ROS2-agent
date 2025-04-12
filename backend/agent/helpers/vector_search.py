from openai import OpenAI
from api_keys import OPENAI_KEY, SUPABASE_KEY, SUPABASE_URL
from supabase import create_client

llm = OpenAI(api_key=OPENAI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def search_robots(user_query: str, threshold: float = 0.7):
    response = llm.embeddings.create(
        input=user_query,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding

    result = supabase.rpc("match_urdfs", {
        "query_embedding": embedding,
        "match_threshold": threshold,
        "match_count": 3
    }).execute()

    if result.error:
        raise RuntimeError(f"Supabase RPC error: {result.error.message}")
    return result.data

