import streamlit as st
import os
from dotenv import load_dotenv

from src.langgraphagenticai.ui.uiconfigfile import Config

# Load OPENAI_API_KEY / TAVILY_API_KEY from .env so the sidebar can stay empty
load_dotenv()

class LoadStreamlitUI:
  """
  Builds the Streamlit sidebar and returns the user's selections as user_controls.
  """
  def __init__(self):
    self.config=Config()
    self.user_controls={}

  def load_streamlit_ui(self):
    page_title = self.config.get_page_title() or ""
    st.set_page_config(page_title="🤖 " + page_title, layout="wide")
    st.header("🤖 " + page_title)
    # Reset each rerun; the Fetch button sets these again on the click that starts AI News
    st.session_state.timeframe = ''
    st.session_state.IsFetchButtonClicked = False

    with st.sidebar:
      # Get options from config (uiconfigfile.ini)
      llm_options = self.config.get_llm_options()
      usecase_options = self.config.get_usecase_options()

      # LLM Selection
      self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

      if self.user_controls["selected_llm"] == 'OpenAI':
        # Model Selection
        model_options = self.config.get_openai_model_options()
        self.user_controls["selected_openai_model"] = st.selectbox("Select Model", model_options)
        # Keep the key in session_state so it survives Streamlit reruns
        self.user_controls["OPENAI_API_KEY"]=st.session_state["OPENAI_API_KEY"]=st.text_input("API Key", type="password")
        # Validate API Key
        if not self.user_controls["OPENAI_API_KEY"]:
          st.warning("⚠️ Please enter your OPENAI API key to proceed !")

      # UseCase Selection
      self.user_controls["selected_usecase"]=st.selectbox("Select Usecases", usecase_options)

      # Tavily Search Selection — needed for web search and the AI News pipeline
      if self.user_controls["selected_usecase"] in ("Chatbot with Tool", "AI News"):
        tavily_key=st.text_input("TAVILY API KEY", type="password")
        self.user_controls["TAVILY_API_KEY"]=st.session_state["TAVILY_API_KEY"]=tavily_key
        if tavily_key:
          os.environ["TAVILY_API_KEY"]=tavily_key

        # Validate API Key (skip the warning if .env already has TAVILY_API_KEY)
        if not self.user_controls["TAVILY_API_KEY"] and not os.environ.get("TAVILY_API_KEY"):
          st.warning("⚠️ Please enter your TAVILY_API_KEY key to proceed")

      if self.user_controls['selected_usecase']=='AI News':
        st.subheader("📰 AI News Explorer")
        
        with st.sidebar:
          time_frame = st.selectbox(
            "🗓️ Select Time Frame",
            ["Daily", "Weekly", "Monthly"],
            index=0
        )

        # main.py reads these flags to run the news graph instead of waiting for chat input
        if st.button("🔍 Fetch the Latest AI News", use_container_width=True):
          st.session_state.IsFetchButtonClicked = True
          st.session_state.timeframe = time_frame

    usecase = self.user_controls.get("selected_usecase") or ""
    st.header("LangGraph: " + usecase)

    return self.user_controls


