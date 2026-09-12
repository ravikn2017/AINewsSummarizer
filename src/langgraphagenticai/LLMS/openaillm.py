import os
import streamlit as st
from langchain_openai import ChatOpenAI

class OpenAiLLM:
  def __init__(self,user_controls_input):
    self.user_controls_input=user_controls_input

  def get_llm_model(self):
    try:
      openai_api_key=self.user_controls_input["OPENAI_API_KEY"]
      selected_openai_model=self.user_controls_input["selected_openai_model"]
      if openai_api_key=='' and os.environ["OPENAI_API_KEY"] =='':
        st.error("Please Enter the OPENAI API KEY")

      llm=ChatOpenAI(api_key=openai_api_key or None,model=selected_openai_model)

    except Exception as e:
      raise ValueError(f"Error Occurred with Exception: {e}")
    return llm