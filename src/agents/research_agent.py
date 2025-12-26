from crewai import Agent
from langchain_openai import ChatOpenAI
from src.tools.web_search_tool import search_web_tool, fetch_webpage_tool
from src.tools.memory_tool import store_memory_tool, retrieve_memory_tool
from src.tools.file_tool import save_to_file_tool


def create_research_agent(model_name="gpt-3.5-turbo", temperature=0.7, verbose=False):
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    tools = [search_web_tool, fetch_webpage_tool, store_memory_tool, 
             retrieve_memory_tool, save_to_file_tool]
    
    return Agent(
        role="Senior Research Analyst",
        goal="Conduct comprehensive web research, gather information from multiple sources, verify facts, and organize findings systematically.",
        backstory="You are an experienced research analyst with expertise in information gathering and analysis. You excel at finding credible sources, cross-referencing information, and extracting actionable insights.",
        tools=tools,
        llm=llm,
        verbose=verbose,
        allow_delegation=True,
        max_iter=10,
        memory=True
    )

