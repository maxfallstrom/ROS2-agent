from urdf_tools.supabase_client import supabase
from urdf_tools.urdf_summarizer import summarize_urdf
from openai import OpenAI

client = OpenAI()

def embed_all_robots():
    robots = supabase.table("urdf_metadata").select("*").execute().data

    for robot in robots:
        if robot.get("embedding"):
            continue

        summary = summarize_urdf(robot)

        response = client.embeddings.create(
            input=summary,
            model="text-embedding-3-small"
        )

        embedding = response.data[0].embedding

        supabase.table("urdf_metadata").update({
            "embedding": embedding
        }).eq("id", robot["id"]).execute()

if __name__ == "__main__":
    embed_all_robots()