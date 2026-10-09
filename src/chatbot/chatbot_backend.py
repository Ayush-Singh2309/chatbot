from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

# os.environ["LANGCHAIN_PROJECT"] = "Chatbot"

model = ChatGoogleGenerativeAI(model = "gemini-3.5-flash-lite")

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    response = model.invoke(state['messages'])
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)
chatbot = graph.compile(checkpointer=checkpointer)

# CONFIG = {"configurable": {"thread_id": "thread-1"}}

# response = chatbot.invoke({'messages': [HumanMessage(content="My name is Ayush")]}, config=CONFIG)
# print(chatbot.get_state(config=CONFIG).values['messages'])

def retrieve_all_threads():
    all_threads = set()
    for c in checkpointer.list(None):
        all_threads.add(c.config['configurable'].get('thread_id'))
    return list(all_threads)

def delete_thread_id(thread_id):
    checkpointer.delete_thread(thread_id)