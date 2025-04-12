import time
from typing import List
from openai import OpenAI
from supabase import create_client
from agent.helpers.api_keys import OPENAI_KEY, SUPABASE_KEY, SUPABASE_URL
from tqdm import tqdm


openai = OpenAI(api_key=OPENAI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_urdf_rows() -> List[dict]:
    response = supabase.table("urdf").select("id, name, summary").execute()
    return response.data

def get_embedding(text: str) -> List[float]:
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def populate_embeddings():
    rows = fetch_urdf_rows()

    for row in tqdm(rows, desc="Embedding URDF summaries"):
        try:
            embedding = get_embedding(row["summary"])

            # Build entry to insert
            insert_data = {
                "id": row["id"],
                "name": row["name"],
                "summary": row["summary"],
                "embeddings": embedding
            }

            supabase.table("urdf_embeddings").upsert(insert_data, on_conflict="id").execute()
            time.sleep(0.5)

        except Exception as e:
            print(f"Failed for ID {row['id']}: {e}")

if __name__ == "__main__":
    populate_embeddings()
