from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search , scrape_url 
from dotenv import load_dotenv
from functools import lru_cache
import os
from pathlib import Path

ENV_PATH = Path(__file__).with_name(".env")
load_dotenv(ENV_PATH, override=True)


def get_env_status(name: str) -> str:
    value = os.getenv(name, "").strip().strip("\"'")
    if value.startswith("replace_with"):
        return "placeholder value still present"
    if value:
        return "present"
    if not ENV_PATH.exists():
        return "missing"
    if ENV_PATH.stat().st_size == 0:
        return "empty"
    return f"present but {name} was not found"


#model setup 
@lru_cache(maxsize=1)
def get_llm():
    env_status = get_env_status("OPENAI_API_KEY")
    if env_status != "present":
        raise RuntimeError(
            "OPENAI_API_KEY is not set to a real key. Replace the placeholder "
            f"value in {ENV_PATH} with your actual OpenAI API key. "
            f"Current .env status: {env_status}."
        )
    return ChatOpenAI(model = "gpt-4o-mini",temperature=0)


#1st agent 
def build_search_agent():
    return create_agent(
        model = get_llm(),
        tools= [web_search]
    )

#2nd agent 

def build_reader_agent():
    return create_agent(
        model = get_llm(),
        tools = [scrape_url]
    )


class LazyChain:
    def __init__(self, prompt):
        self.prompt = prompt

    def invoke(self, inputs):
        chain = self.prompt | get_llm() | StrOutputParser()
        return chain.invoke(inputs)


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = LazyChain(writer_prompt)

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = LazyChain(critic_prompt)
