from crewai import Agent
from langchain_openai import ChatOpenAI
from src.tools.memory_tool import retrieve_memory_tool
from src.tools.file_tool import save_to_file_tool, load_from_file_tool


def create_summary_agent(model_name="gpt-3.5-turbo", temperature=0.5, verbose=False):
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    tools = [retrieve_memory_tool, save_to_file_tool, load_from_file_tool]
    
    return Agent(
        role="Executive Summary Specialist",
        goal="Transform research findings into clear, concise, and actionable executive summaries with strategic recommendations.",
        backstory="You are a skilled communication expert who specializes in creating executive summaries for senior leadership. You understand how to prioritize information and translate research into actionable intelligence.",
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=False,
        max_iter=5,
        memory=True
    )

