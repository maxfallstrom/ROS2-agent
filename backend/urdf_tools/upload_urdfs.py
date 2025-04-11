import os
import uuid
import csv
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from robot_descriptions.loaders.yourdfpy import load_robot_description
from urdf_tools.urdf_summarizer import summarize_robot, generate_description, generate_tags
from typing import List
import asyncio

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CSV_FILE_PATH = "urdf_tools/files/robot_names.csv"


def embed_summary(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def upload_robot(row: dict):
    robot_name = row["Name"]
    print(f"> Loading {robot_name}...")

    summary = summarize_robot(robot_name)
    described_robot = generate_description(summary, row)
    tags = generate_tags(described_robot)
    embedding = embed_summary(described_robot)
    robot_id = uuid.uuid4()

    urdf_result = await add_db_row(robot_id, summary, row, tags)

    if urdf_result.error:
        raise Exception(f"Error uploading URDF: {urdf_result.error}")

    embedding_result = await add_vector_row(robot_id, embedding)

    if embedding_result.error:
        raise Exception(f"Error uploading embedding: {embedding_result.error}")

    print(f"Uploaded {robot_name} (id: {robot_id})")


async def add_vector_row(robot_id: uuid, embedding: List[float]):
    return await supabase.table("urdf_embeddings").insert({
        "id": robot_id,
        "embedding": embedding
    }).execute()

async def add_db_row(robot_id: uuid, summary: dict, row: dict, tags: list):
    return await supabase.table("urdf").insert({
        "id": robot_id,
        "name": row["Robot"],
        "maker": row["Maker"],
        "type": row["Type"],
        "dof": summary["dof"] if summary["dof"] != 0 else row["DOF"],
        "total_mass": summary["total_mass"],
        "has_manipulator": summary["has_manipulator"],
        "num_manipulator": summary["num_manipulators"],
        "manipulators": summary["manipulator_names"],
        "links": summary["links"],
        "joints": summary["joints"],
        "num_joints": summary["total_joints"],
        "num_links": summary["total_links"],
        "tags": tags,
        "summary": summary,
        "urdf_uri": ""
    }).execute()


async def main():
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            if row["Format"] != "URDF":
                continue
            try:
                await upload_robot(row)
            except Exception as e:
                print(f"Failed for {row['Name']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
