from langchain_core.messages import HumanMessage
import streamlit as st
from src.chatbot.chatbot_backend import chatbot, retrieve_all_threads, delete_thread_id
import uuid

# Functions

def generate_new_thread_id():
    return f"Thread - {uuid.uuid4()}"

def reset_chat():
    st.session_state['thread_id'] = generate_new_thread_id()
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    st.session_state['thread_id'] = thread_id
    messages = chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values.get('messages', [])
    temp_messages = []
    for message in messages:
        if isinstance(message, HumanMessage):
            temp_messages.append({'role': 'user', 'content': message.content})
        else:
            temp_messages.append({'role': 'assistant', 'content': message.text})
    return temp_messages

# Initialise

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_new_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

add_thread(st.session_state['thread_id'])

# Side Bar

st.sidebar.title("LangGraph ChatBot")
st.sidebar.button("New Chat", on_click=reset_chat)
st.sidebar.header("My Conversations")
with st.sidebar:
    for thread in st.session_state['chat_threads'][::-1]:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(thread, key=f"{thread}", use_container_width=True):
                st.session_state['message_history'] = load_conversation(thread)
        with col2:
            if st.button("🗑️", key=f"delete_{thread}", help="Delete this thread"):
                delete_thread_id(thread)
                if thread in st.session_state['chat_threads']:
                    st.session_state['chat_threads'].remove(thread)
                if st.session_state['thread_id'] == thread:
                    if st.session_state['chat_threads']:
                        st.session_state['thread_id'] = st.session_state['chat_threads'][-1]
                        st.session_state['message_history'] = load_conversation(st.session_state['thread_id'])
                    else:
                        reset_chat()
                       
                st.rerun()

for message in st.session_state['message_history']:
    st.chat_message(message['role']).write(message['content'])

CONFIG = {
    'configurable': {'thread_id': st.session_state['thread_id']},
    'metadata': {'thread_id': st.session_state['thread_id']},
    'run_name': 'chat_run'
}

user_input = st.chat_input('Type here...')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    st.chat_message('user').write(user_input)

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_content.text for message_content, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]}, 
            config=CONFIG,
            stream_mode="messages"
        )
    )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})