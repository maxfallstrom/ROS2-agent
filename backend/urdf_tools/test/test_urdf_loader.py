import pandas as pd
from urdf_tools.urdf_summarizer import summarize_robot
import json

# File if we want to loop or something
#df = pd.read_csv(filepath_or_buffer="../files/robot_names.csv", delimiter=";")

#first_robot_name = df.iloc[1]["Name"]
#print(f"Attempting to load robot: {first_robot_name}")
######


def test_urdf_summarizer():
    # Just testing Baxter for now
    return summarize_robot("elf2_description")

print(json.dumps(test_urdf_summarizer(), indent=2))



