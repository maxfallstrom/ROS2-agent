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
import aiofiles
import zipfile
from pathlib import Path
from io import BytesIO

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET_URL = f"{SUPABASE_URL}/storage/v1/object/public/robotbucket"

OPENAI_KEY = os.getenv("OPENAI_KEY")

ROBOT_FOLDER_ROOT = "urdf_tools/robots"
CSV_FILE_PATH = "urdf_tools/files/robot_names.csv"

openai_client = OpenAI(api_key=OPENAI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def embed_summary(text: str):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

async def upload_robot_folder_to_bucket(robot_name: str, folder_path: str, bucket_name: str = "robotbucket") -> str:
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in Path(folder_path).rglob("*"):
            if path.is_file():
                arcname = path.relative_to(folder_path)
                zipf.write(path, arcname)

    zip_data = zip_buffer.getvalue()

    object_path = f"{robot_name}.zip"

    response = await supabase.storage.from_(bucket_name).upload(
        path=object_path,
        file=zip_data,
        file_options={"content-type": "application/zip", "upsert": True}
    )

    if hasattr(response, "error") and response.error:
        raise Exception(f"Upload failed for {robot_name}: {response.error}")

    print(f"Uploaded ZIP: {object_path} to bucket '{bucket_name}'")
    return object_path


async def upload_robot_image(image_path: str, robot_name: str) -> str | None:
    if not os.path.exists(image_path):
        print(f"Image not found for {robot_name}, skipping image upload.")
        return None

    supabase_path = f"{robot_name}.png"

    with open(image_path, "rb") as f:
        data = f.read()

    response = await supabase.storage.from_("robotpicturesbucket").upload(
        path=supabase_path,
        file=data,
        file_options={"content-type": "image/png", "upsert": True}
    )

    if hasattr(response, "error") and response.error:
        print(f"Error uploading image for {robot_name}: {response.error}")
        return None

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/robotpicturesbucket/{supabase_path}"
    print(f"Uploaded image for {robot_name} to {public_url}")
    return public_url


async def upload_robot(row: dict):
    robot_name = row["Name"]
    print(f"> Loading {robot_name}...")

    summary = summarize_robot(robot_name)
    described_robot = generate_description(summary, row)
    tags = generate_tags(described_robot)
    embedding = embed_summary(described_robot)
    robot_id = str(uuid.uuid4())

    folder_path = os.path.join("urdf_tools", "robots", robot_name)
    object_path = await upload_robot_folder_to_bucket(robot_name, folder_path)
    urdf_url = f"{SUPABASE_BUCKET_URL}/{object_path}"

    image_path = os.path.join("urdf_tools", "robots", "images", f"{robot_name}.png")
    image_url = await upload_robot_image(image_path, robot_name)

    urdf_result = await add_db_row(robot_id, summary, row, tags, described_robot, urdf_url, image_url)

    if urdf_result.error:
        raise Exception(f"Error uploading URDF: {urdf_result.error}")

    embedding_result = add_vector_row(robot_id, embedding)

    if embedding_result.error:
        raise Exception(f"Error uploading embedding: {embedding_result.error}")

    print(f"Uploaded {robot_name} (id: {robot_id})")


def add_vector_row(robot_id: str, embedding: List[float]):
    return supabase.table("urdf_embeddings").insert({
        "id": robot_id,
        "embedding": embedding
    }).execute()

async def add_db_row(robot_id: str, summary: dict, row: dict, tags: list, decribed_robot: str, urdf_url: str, image_url: str):
    return await supabase.table("urdf").insert({
        "id": robot_id,
        "name": row["Robot"],
        "maker": row["Maker"],
        "type": row["Type"],
        "dof": summary["dof"] if summary["dof"] != 0 else row["DOF"],
        "total_mass": summary["total_mass"],
        "has_manipulator": summary["has_manipulator"],
        "num_manipulators": summary["num_manipulators"],
        "manipulators": summary["manipulator_names"],
        "links": summary["links"],
        "joints": summary["joints"],
        "num_joints": summary["total_joints"],
        "num_links": summary["total_links"],
        "tags": tags,
        "summary": decribed_robot,
        "urdf_uri": urdf_url,
        "image_uri": image_url,
    }).execute()


async def main():
    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            if row["Format"] != "URDF":
                continue

            robot_name = row["Name"]
            robot_folder_path = os.path.join(ROBOT_FOLDER_ROOT, robot_name)

            if not os.path.isdir(robot_folder_path):
                continue

            try:
                await upload_robot(row)
            except Exception as e:
                print(f"Failed for {robot_name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
