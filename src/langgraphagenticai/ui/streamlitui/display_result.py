import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json

class DisplayResultsStreamlit:
  """
  Renders graph output in Streamlit. The layout depends on the selected use case.
  """
  def __init__(self,usecase,graph,user_message):
    # usecase: sidebar selection; graph: compiled LangGraph; user_message: chat text or news time frame
    self.usecase = usecase
    self.graph = graph
    self.user_message = user_message

  def display_result_on_ui(self):
    usecase = self.usecase
    graph = self.graph
    user_message = self.user_message
    if usecase == "Basic Chatbot":
      # Stream tokens/events so the reply appears as the chatbot node finishes
      for event in graph.stream({'messages':("user",user_message)}):
        print(event.values())
        for value in event.values():
          print(value['messages'])
          with st.chat_message("user"):
            st.write(user_message)
          with st.chat_message("assistant"):
            st.write(value['messages'].content)

    elif usecase == "Chatbot with Tool":
      # Prepare state and invoke the graph
      # invoke() runs the full loop: chatbot -> optional Tavily tool -> chatbot
      initial_state = {"messages": [user_message]}
      res = graph.invoke(initial_state)
      # Walk the message history so the user sees the question, tool output, and final answer
      for message in res['messages']:
        if type(message) == HumanMessage:
          with st.chat_message("user"):
            st.write(message.content)
        elif type(message)==ToolMessage:
          with st.chat_message("ai"):
            st.write("Tool Call Start")
            st.write(message.content)
            st.write("Tool Call End")
        elif type(message)==AIMessage and message.content:
          with st.chat_message("assistant"):
            st.write(message.content)

    elif usecase == "AI News":
      # user_message here is Daily / Weekly / Monthly from the Fetch button
      frequency = self.user_message
      # save_result writes this same path: ./AINews/{frequency}_summary.md
      AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
      with st.spinner("Fetching and summarizing news... ⏳"):
        result = graph.invoke({"messages": frequency})
        try:
          # Read the markdown file produced by the save_result node
          with open(AI_NEWS_PATH, "r") as file:
            markdown_content = file.read()

          # Display the markdown content in Streamlit
          st.markdown(markdown_content, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")