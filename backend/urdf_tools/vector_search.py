from openai import OpenAI
from urdf_tools.supabase_client import supabase

client = OpenAI()

def search_robots(user_query: str, threshold: float = 0.7):
    response = client.embeddings.create(
        input=user_query,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding

    result = supabase.rpc("match_urdfs", {
        "query_embedding": embedding,
        "match_threshold": threshold,
        "match_count": 5
    }).execute()

    print("Top Matches:")
    for match in result.data:
        print(f"{match['name']} (score: {match['similarity']:.2f})")

if __name__ == "__main__":
    search_robots("I need a robot to navigate in farms and carry tools")