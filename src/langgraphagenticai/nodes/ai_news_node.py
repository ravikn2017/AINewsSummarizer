from time import timezone
from typing import Literal
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate

class AINewsNode:
  """
  LangGraph nodes for the AI News pipeline: fetch, summarize, save.
  """
  def __init__(self,llm):
    """
    Initialize the AINewsNode with API keys for Tavily and OpenAI
    """

    self.tavily = TavilyClient()
    self.llm=llm
    # This is used to capture various steps in this file so that later can be use for steps shown
    self.state = {}

  def fetch_news(self, state):
    """
    Fetch AI News based on the specified frequency

    Args:
      state (dict): The state dictionary containing 'frequency'

    Returns:
      dict: Updated state with 'news_data' key containing fetched news
    """
    # Frequency comes from the UI time frame (Daily / Weekly / Monthly)
    frequency = state["messages"][0].content.lower()
    self.state["frequency"] = frequency
    time_range_map: dict[str, Literal["day", "week", "month", "year"]] = {
      "daily": "day",
      "weekly": "week",
      "monthly": "month",
      "year": "year",
    }
    days_map = {"daily": 1, "weekly": 7, "monthly": 30, "year": 366}

    # Tavily news search scoped to the selected time range
    response = self.tavily.search(
      query="Top Artificial Intelligence (AI) technology news globally and in India",
      topic="news",
      time_range=time_range_map[frequency],
      include_answer="advanced",
      max_results=15,
      days=days_map[frequency],
    )

    state["news_data"] = response.get("results", [])
    self.state["news_data"] = state["news_data"]
    return state

  def summarize_news(self, state):
    """
    Summarize the fetched news using an LLM

    Args:
      state (dict): The state dictionary containing 'news_data'.

    Returns:
      dict: Updated state with 'summary' key containing the summaried news
    """

    news_items = self.state['news_data']

    # Ask the LLM to turn Tavily results into dated markdown bullets
    prompt_template = ChatPromptTemplate.from_messages([
      ("system", """Summarize AI news articles into markdown format. For each item include:
      - Date in **YYYY-MM-DD** format in IST timezone
      - Concise sentences summary from latest news
      - Sort news by date wise (latest first)
      - Source URL as link
      Use format:
      ### [Date]
      - [Summary](URL)"""),
      ("user", "Articles:\n{articles}")
    ])

    articles_str = "\n\n".join([
        f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
        for item in news_items
    ])

    response = self.llm.invoke(prompt_template.format(articles=articles_str))
    state["summary"] = response.content
    self.state["summary"] = state["summary"]
    return self.state

  def save_result(self, state):
    """
    Write the markdown summary to ./AINews/{frequency}_summary.md
    """
    frequency = self.state["frequency"]
    summary = self.state["summary"]
    import os
    os.makedirs("./AINews", exist_ok=True)
    filename = f"./AINews/{frequency}_summary.md"
    with open(filename, "w") as f:
      f.write(f"# {frequency.capitalize()} AI News Summary\n\n")
      f.write(summary)
    self.state["filename"] = filename
    return self.state