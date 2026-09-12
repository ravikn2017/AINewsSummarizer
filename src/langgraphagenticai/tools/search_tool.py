import os
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

load_dotenv()

def get_tools():
  """
  Return the list of tools to be used in the chatbot
  """
  tools=[TavilySearch(max_results=2, tavily_api_key=os.environ.get("TAVILY_API_KEY"))]
  return tools

def create_tool_node(tools):
  """
  Creates and returns a tool node for the graph
  """
  return ToolNode(tools=tools)

