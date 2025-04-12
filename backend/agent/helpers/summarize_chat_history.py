from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agent.helpers.api_keys import OPENAI_KEY

llm = ChatOpenAI(api_key=OPENAI_KEY, temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a summarizer for a robotics search engine.\n"
     "Your job is to extract a concise, 100-word description of what kind of robot the user needs, "
     "based on the chat conversation so far.\n\n"
     "The summary should be clear, focused, and suitable for semantic search."),
    ("human", "{conversation}")
])

async def summarize_context_for_embedding(messages: List[Dict[str, str]]) -> str:
    
    conversation = "\n".join(
        f"{msg['role']}: {msg['content']}" for msg in messages
    )

    formatted_prompt = await prompt.ainvoke({"conversation": conversation})
    response = await llm.ainvoke(formatted_prompt)

    return response.content.strip()