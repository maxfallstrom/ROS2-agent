from openai import OpenAI
from yourdfpy import URDF, Robot
from robot_descriptions.loaders.yourdfpy import load_robot_description

client = OpenAI()

def generate_tags(summary: str) -> list:
    prompt = (
        "Given the following description of a robot, extract 3–6 relevant domain tags. "
        "Tags should describe the environments or applications this robot is likely used in. "
        "Use lowercase, one-word or hyphenated tags like: agriculture, warehouse, drone-inspection, home, education, heavy-lifting, etc.\n\n"
        f"Robot description:\n{summary}\n\n"
        "Tags (as a Python list of strings):"
        "Do not return anything else at all, just a string like ['agriculture', 'warehouse'] and if you cannot come up with anything just return empty brackets []"
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.3
    )

    tag_string = response.output[0].content[0].text.strip()

    return tag_string

def generate_description(summary: dict, row: dict):
    prompt = (
        "You are a robotics expert, and specialize in giving descriptions on robots given a robot and it's properties"
        "Given the following robot, describe it and what it might be useful for in 100 words"
        f"Robot name:\n{row["Robot"]}\n"
        f"Robot maker:\n{row["Maker"]}\n"
        f"Robot Type:\n{row["Type"]}\n"
        f"Robot description:\n{summary}\n"
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        temperature=0.3
    )

    description = response.output[0].content[0].text.strip()

    return description



def find_leaf_links(urdf: Robot):
    """Find all links that are not parent to any joint (end effectors)."""
    child_links = {joint.child for joint in urdf.joints}
    parent_links = {joint.parent for joint in urdf.joints}
    return list(child_links - parent_links)

def trace_chain_to_base(urdf: Robot, end_link_name: str):
    """Trace the kinematic chain from a leaf back to the root."""
    chain = []
    current_link = end_link_name
    while True:
        for joint in urdf.joints:
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

def get_manipulator_chains(urdf: Robot):
    """Return all detected manipulator joint chains."""
    leaf_links = find_leaf_links(urdf)
    manipulators = []
    for leaf in leaf_links:
        chain = trace_chain_to_base(urdf, leaf)
        if is_probable_manipulator(chain):
            manipulators.append(chain)
    return manipulators

def summarize_robot(name: str):
    robot = load_robot_description(name)
    urdf = robot.robot
    summary = {
        "name": urdf.name,
        "total_links": len(urdf.links),
        "total_joints": len(urdf.joints),
        "dof": len(robot.actuated_joint_names),
        "has_manipulator": False,
        "num_manipulators": 0,
        "manipulator_names": [],
        "total_mass_estimate": sum((link.inertial.mass if link.inertial and link.inertial.mass else 0.0) for link in urdf.links),
    }

    manipulator_chains = get_manipulator_chains(urdf)
    summary["num_manipulators"] = len(manipulator_chains)
    summary["has_manipulator"] = len(manipulator_chains) > 0
    summary["manipulator_names"] = [chain[-1].child for chain in manipulator_chains]

    return summary