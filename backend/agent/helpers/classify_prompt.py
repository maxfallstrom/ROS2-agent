from pydantic import BaseModel
from typing import Literal
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AgentState
from agent.helpers.api_keys import OPENAI_KEY

class PromptClassification(BaseModel):
    status: Literal["complete", "incomplete"]
    question: str = None

parser = PydanticOutputParser(pydantic_object=PromptClassification)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a robotics assistant. A user is trying to find a robot for their needs. We need information about the task, environment, and capabilities of the robot.\n"
     "Here is the latest response:\n{input}\n\n"
     "Here is the info gathered so far:\n{collected_info_str}\n\n"
     "Decide if you now have enough info to choose a robot."
     "If yes, return 'comlete' and no follow-up question is needed."
     "If not, return 'incomplete' and include a follow-up question to ask."
     "Respond in JSON format with a `status` and optional a follow up `question`."),
    ("human", "Classify this.")
])

llm = ChatOpenAI(api_key=OPENAI_KEY, temperature=0)

def format_collected_info(messages: list[str]) -> str:
    return "\n".join(f"- {msg}" for msg in messages)


async def classify_prompt(state: AgentState):
    user_input = state["messages"][-1]["content"]
    messages = state.get("messages", [])
    collected_info = [msg["content"] for msg in messages if msg.get("role") == "user"]
    collected_info_str = format_collected_info(collected_info)


    formatted_prompt = await prompt.ainvoke({
        "input": user_input,
        "collected_info_str": collected_info_str
    })

    raw_response = await llm.ainvoke(formatted_prompt)

    parsed: PromptClassification = parser.invoke(raw_response)

    return parsed

