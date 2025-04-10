import pandas as pd
from urdf_summarizer import summarize_robot

df = pd.read_csv(filepath_or_buffer="../files/robot_names.csv", delimiter=";")

first_robot_name = df.iloc[1]["Name"]
print(f"Attempting to load robot: {first_robot_name}")

#robot = load_robot_description("baxter_description")

summary = summarize_robot("baxter_description")

print(summary)

