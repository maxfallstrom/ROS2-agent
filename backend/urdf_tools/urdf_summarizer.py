from openai import OpenAI
from yourdfpy import URDF, Robot
from robot_descriptions.loaders.yourdfpy import load_robot_description
from urdf_tools.helpers.urdf_helpers import try_float
import json
from typing import List

client = OpenAI()

def generate_tags(summary: str) -> List[str]:
    prompt = (
        "Given the following description of a robot, extract 3–6 relevant domain tags. "
        "Tags should describe the environments or applications this robot is likely used in. "
        "Use lowercase, one-word or hyphenated tags like: agriculture, warehouse, drone-inspection, home, education, heavy-lifting, etc."
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": "You are an expert in structured data extraction."},
            {"role": "user", "content": f"{prompt}\n\nRobot description:\n{summary}"}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "extract_robot_tags",
                "schema": {
                    "type": "object",
                    "properties": {
                        "tags": {
                            "type": "array",
                            "items": { "type": "string" }
                        }
                    },
                    "required": ["tags"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        temperature=0.3
    )

    tags = response.output_text
    return json.loads(tags)["tags"]

def generate_description(summary: dict, row: dict):
    prompt = (
        "You are a robotics expert, and specialize in giving descriptions on robots given a robot and it's properties"
        "Given the following robot, describe it and what it might be useful for in 100 words"
        f"Robot name:\n{row['Robot']}\n"
        f"Robot maker:\n{row['Maker']}\n"
        f"Robot Type:\n{row['Type']}\n"
        f"Robot description:\n{summary}\n"
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.3
    )

    description = response.output_text

    return description



def find_leaf_links(robot: Robot):
    """Find all links that are not parent to any joint (end effectors)."""
    child_links = {joint.child for joint in robot.joints}
    parent_links = {joint.parent for joint in robot.joints}
    return list(child_links - parent_links)

def trace_chain_to_base(robot: Robot, end_link_name: str):
    """Trace the kinematic chain from a leaf back to the root."""
    chain = []
    current_link = end_link_name
    while True:
        for joint in robot.joints:
            if joint.child == current_link:
                chain.insert(0, joint)
                current_link = joint.parent
                break
        else:
            break
    return chain

def is_probable_manipulator(chain: list):
    """Use simple heuristics on a joint chain to decide if it's a manipulator."""
    num_dof = sum(1 for joint in chain if joint.type in ["revolute", "prismatic"])
    end_effector_name = chain[-1].child if chain else ""
    return num_dof >= 4 or any(key in end_effector_name.lower() for key in ["hand", "gripper", "tool"])

def get_manipulator_chains(robot: Robot):
    """Return all detected manipulator joint chains."""
    leaf_links = find_leaf_links(robot)
    manipulators = []
    for leaf in leaf_links:
        chain = trace_chain_to_base(robot, leaf)
        if is_probable_manipulator(chain):
            manipulators.append(chain)
    return manipulators

def summarize_robot(name: str):
    urdf = load_robot_description(name)
    robot = urdf.robot
    summary = {
        "name": robot.name,
        "total_links": len(robot.links),
        "total_joints": len(robot.joints),
        "links": [],
        "joints": [],
        "dof": len(urdf.actuated_joint_names),
        "has_manipulator": False,
        "num_manipulators": 0,
        "manipulator_names": [],
        "total_mass": sum((link.inertial.mass if link.inertial and link.inertial.mass else 0.0) for link in robot.links),
    }

    joints = extract_joints(robot)
    links = extract_links(robot)
    summary["joints"] = joints
    summary["links"] = links

    manipulator_chains = get_manipulator_chains(robot)
    summary["num_manipulators"] = len(manipulator_chains)
    summary["has_manipulator"] = len(manipulator_chains) > 0
    summary["manipulator_names"] = [chain[-1].child for chain in manipulator_chains]

    return summary

def extract_links(robot: Robot):
    links = []
    for link in robot.links:
        inertial = link.inertial
        mass = inertial.mass if inertial and inertial.mass else 0.0
        inertia = {
            "ixx": 0, "ixy": 0, "ixz": 0,
            "iyx": 0, "iyy": 0, "iyz": 0,
            "izx": 0, "izy": 0, "izz": 0,
        }

        if inertial and inertial.inertia.any():
            inertia = {
                "ixx": try_float(inertial.inertia[0][0]),
                "ixy": try_float(inertial.inertia[0][1]),
                "ixz": try_float(inertial.inertia[0][2]),
                "iyx": try_float(inertial.inertia[1][0]),
                "iyy": try_float(inertial.inertia[1][1]),
                "iyz": try_float(inertial.inertia[1][2]),
                "izx": try_float(inertial.inertia[2][0]),
                "izy": try_float(inertial.inertia[2][1]),
                "izz": try_float(inertial.inertia[2][2])
            }

        links.append({
            "name": link.name,
            "mass": mass,
            #"inertia": inertia,
            "has_visual": bool(link.visuals),
            "has_collision": bool(link.collisions),
        })
    return links

def extract_joints(robot: Robot):
    joints = []
    for joint in robot.joints:
        joint_data = {
            "name": joint.name,
            "type": joint.type,
            "parent": joint.parent,
            "child": joint.child,
        }
        if joint.limit:
            joint_data["limits"] = {
                "lower": joint.limit.lower or 0,
                "upper": joint.limit.upper or 0,
                "effort": joint.limit.effort or 0,
                "velocity": joint.limit.velocity or 0,
            }
        joints.append(joint_data)
    return joints



