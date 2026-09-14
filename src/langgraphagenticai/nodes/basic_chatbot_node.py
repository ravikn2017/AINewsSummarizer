from src.langgraphagenticai.state.state import State

class BasicChatbotNode:
  """
  Basic Chatbot login implementation
  """
  def __init__(self,model):
    self.llm=model

  def process(self,state:State)->dict:
    """
    Processes the input state and generates a chatbot response
    """
    # Return an AI message; add_messages appends it to state["messages"]
    return {"messages":self.llm.invoke(state['messages'])}
