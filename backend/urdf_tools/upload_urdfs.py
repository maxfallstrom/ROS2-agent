import os
import uuid
import csv
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
from robot_descriptions.loaders.yourdfpy import load_robot_description
from urdf_summarizer import summarize_robot, generate_description, generate_tags

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OPENAI_KEY = os.environ["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=OPENAI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CSV_FILE_PATH = "files/robot_names.csv"


def embed_summary(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def upload_robot(row: dict):
    robot_name = row["Name"]
    print(f"> Loading {robot_name}...")

    try:
        robot = load_robot_description(robot_name)
    except Exception as e:
        print(f"Failed loading robot {robot_name}")

    summary = summarize_robot(robot)
    described_robot = generate_description(summary, row)
    tags = generate_tags(described_robot)
    embedding = embed_summary(described_robot)
    robot_id = uuid.uuid4()

    urdf_result = supabase.table("urdf").insert({
        "id": robot_id,
        "name": row["Robot"],
        "maker": row["Maker"],
        "locomotion_type": row["Type"],
        "dof": summary["dof"] if summary["dof"] != 0 else row["DOF"],
        "total_mass": summary["total_mass"],
        "manipulator": summary["has_manipulator"],
        "num_joints": summary["total_joints"],
        "num_links": summary["total_links"],
        "tags": tags,
        "summary": summary,
        "urdf_uri": ""
    }).execute()

    if urdf_result.error:
        raise Exception(f"Error uploading URDF: {urdf_result.error}")

    embedding_result = supabase.table("urdf_embeddings").insert({
        "id": robot_id,
        "embedding": embedding
    }).execute()

    if embedding_result.error:
        raise Exception(f"Error uploading embedding: {embedding_result.error}")

    print(f"Uploaded {robot_name} (id: {robot_id})")


if __name__ == "__main__":
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            if row["Format"] != "URDF":
                continue
            try:
                upload_robot(row)
            except Exception as e:
                print(f"Failed for {row['name']}: {e}")
