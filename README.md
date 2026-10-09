# LangGraph Chatbot

A conversational AI chatbot built with **LangGraph, Google Gemini, LangChain, Streamlit, and SQLite**.

The application provides a ChatGPT-style interface with **persistent conversation threads**, allowing users to create multiple conversations, switch between previous conversations, continue chats from where they left off, and delete conversations.

The backend uses **LangGraph's stateful graph architecture** and **SQLite checkpointing** to persist conversation state across sessions.

---

## 🚀 Features

- 💬 Conversational AI powered by **Google Gemini**
- 🧠 Persistent conversation memory using **LangGraph checkpoints**
- 🗂️ Multiple independent conversation threads
- 🔄 Resume previous conversations
- ➕ Create new conversations
- 🗑️ Delete individual conversations
- 💾 SQLite-based persistent storage
- ⚡ Streaming AI responses in the Streamlit UI
- 🖥️ Interactive ChatGPT-style interface using Streamlit
- 🧩 Graph-based backend architecture using LangGraph

---

## 🏗️ Architecture

The application consists of two primary layers:

```text
┌───────────────────────────────┐
│        Streamlit UI           │
│                               │
│  • Chat Interface             │
│  • Conversation Sidebar       │
│  • New Chat                   │
│  • Load Conversation          │
│  • Delete Conversation        │
└───────────────┬───────────────┘
                │
                │ User Message
                ▼
┌───────────────────────────────┐
│        LangGraph Backend      │
│                               │
│       START                   │
│         │                     │
│         ▼                     │
│    ┌───────────┐              │
│    │ chat_node │              │
│    └─────┬─────┘              │
│          │                    │
│          ▼                    │
│         END                   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Google Gemini           │
│                               │
│    ChatGoogleGenerativeAI     │
└───────────────────────────────┘
                │
                ▼
┌───────────────────────────────┐
│       SQLite Checkpointer     │
│                               │
│       chatbot.db              │
│                               │
│  • Messages                   │
│  • Thread State               │
│  • Conversation History       │
└───────────────────────────────┘
```

---

## 🔄 How It Works

### 1. User starts a conversation

When the application starts, a unique thread ID is generated:

```python
def generate_new_thread_id():
    return f"Thread - {uuid.uuid4()}"
```

Each conversation therefore gets its own unique identifier.

---

### 2. User sends a message

The Streamlit frontend converts the user input into a LangChain `HumanMessage`:

```python
HumanMessage(content=user_input)
```

The message is then passed to the LangGraph chatbot along with the current thread configuration.

```python
CONFIG = {
    "configurable": {
        "thread_id": st.session_state["thread_id"]
    }
}
```

The `thread_id` tells LangGraph which conversation state should be used.

---

### 3. LangGraph processes the message

The backend defines a simple graph:

```text
START
  │
  ▼
chat_node
  │
  ▼
 END
```

The `chat_node` sends the conversation history to Gemini:

```python
def chat_node(state: ChatState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}
```

The updated messages are returned to the graph state.

---

### 4. Conversation state is persisted

The graph is compiled with a SQLite checkpointer:

```python
conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn=conn)

chatbot = graph.compile(
    checkpointer=checkpointer
)
```

This allows LangGraph to persist state associated with individual thread IDs.

For example:

```text
Thread - abc123
    ├── User message
    ├── Assistant response
    ├── User message
    └── Assistant response

Thread - xyz456
    ├── User message
    ├── Assistant response
    └── ...
```

This provides independent conversation histories for different threads.

---

## 🧠 Conversation Management

The application maintains a list of available conversation threads using:

```python
def retrieve_all_threads():
    all_threads = set()

    for c in checkpointer.list(None):
        all_threads.add(
            c.config["configurable"].get("thread_id")
        )

    return list(all_threads)
```

Users can then:

### Create a new chat

Click **New Chat** to generate a new thread.

### Switch conversations

Selecting an existing thread loads its persisted messages:

```python
chatbot.get_state(
    config={
        "configurable": {
            "thread_id": thread_id
        }
    }
)
```

### Delete a conversation

A thread can be permanently removed using:

```python
delete_thread_id(thread_id)
```

which internally calls:

```python
checkpointer.delete_thread(thread_id)
```

---

## ⚡ Streaming Responses

The application streams model responses rather than waiting for the entire response to be generated.

```python
chatbot.stream(
    {"messages": [HumanMessage(content=user_input)]},
    config=CONFIG,
    stream_mode="messages"
)
```

The response is then rendered incrementally in Streamlit:

```python
st.write_stream(...)
```

This provides a more responsive chat experience.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Application development |
| **LangGraph** | Stateful chatbot workflow |
| **LangChain** | LLM/message abstractions |
| **Google Gemini** | Large Language Model |
| **Streamlit** | Web-based chat interface |
| **SQLite** | Persistent conversation storage |
| **python-dotenv** | Environment variable management |
| **UUID** | Unique conversation/thread IDs |

---

## 📁 Project Structure

A suitable project structure for this implementation is:

```text
langgraph-chatbot/
│
├── src/
│   └── chatbot/
│       ├── __init__.py
│       └── chatbot_backend.py
│       └── streamlit.py
│
├── chatbot.db
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Components

#### `app.py`

Streamlit frontend responsible for:

- Rendering the chat interface
- Managing Streamlit session state
- Creating new conversations
- Loading existing conversations
- Deleting conversations
- Streaming model responses

#### `src/chatbot/chatbot_backend.py`

Backend responsible for:

- Initializing Gemini
- Defining the LangGraph state
- Creating the chatbot graph
- Configuring SQLite checkpointing
- Retrieving conversation threads
- Deleting conversation threads

#### `chatbot.db`

SQLite database used by the LangGraph checkpointer to persist conversation state.

> **Note:** The database is generated locally when the application runs. It should generally not be committed to GitHub if it contains personal conversation data.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git

cd <your-repository>
```

---

## 2. Create a virtual environment

### macOS / Linux

```bash
python -m venv .venv

source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

A typical `requirements.txt` for this project would contain:

```text
langchain
langchain-core
langchain-google-genai
langgraph
langgraph-checkpoint-sqlite
streamlit
python-dotenv
```

---

# 🔑 Environment Variables

The application requires a Google Gemini API key.

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

The application loads environment variables using:

```python
from dotenv import load_dotenv

load_dotenv()
```

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

**Never commit your API key to GitHub.**

---

# ▶️ Running the Application

Start the Streamlit application:

```bash
python -m streamlit run src/chatbot/streamlit.py
```

Streamlit will provide a local URL similar to:

```text
http://localhost:8501
```

Open the URL in your browser to use the chatbot.

---

# 💬 Example Usage

A typical interaction looks like:

```text
User:
My name is Ayush.

Assistant:
Nice to meet you, Ayush! How can I help you today?

User:
What is LangGraph?

Assistant:
LangGraph is a framework for building stateful...
```

The conversation is associated with the current thread ID and persisted through SQLite.

If the user creates another conversation:

```text
Thread - abc123
    └── Previous conversation

Thread - xyz456
    └── New conversation
```

The two conversations remain independent.

---

# 🧩 LangGraph State

The chatbot uses a typed state object:

```python
class ChatState(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        add_messages
    ]
```

The `messages` field stores the conversation messages.

`add_messages` allows LangGraph to append new messages to the existing state rather than replacing the entire message history.

Conceptually:

```text
Initial State
    ↓
messages = []

User message
    ↓
messages = [HumanMessage]

LLM response
    ↓
messages = [
    HumanMessage,
    AIMessage
]
```

As additional turns occur, the state continues to accumulate messages within the thread.

---

# 🔀 Graph Design

Although the current chatbot has a simple workflow, it is deliberately implemented using LangGraph.

```python
graph = StateGraph(ChatState)

graph.add_node(
    "chat_node",
    chat_node
)

graph.add_edge(
    START,
    "chat_node"
)

graph.add_edge(
    "chat_node",
    END
)
```

This provides a foundation for extending the application into a more sophisticated agentic workflow.

For example:

```text
                  ┌──────────────┐
                  │ User Query   │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Query Router │
                  └──────┬───────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Search      Tool       Direct
           Node        Node       Response
              │          │          │
              └──────────┼──────────┘
                         ▼
                  ┌──────────────┐
                  │ LLM Response │
                  └──────────────┘
```

---

# 🎯 Key Engineering Concepts Demonstrated

This project demonstrates practical implementation of several modern LLM application concepts:

### Stateful LLM Applications

The chatbot maintains conversation state instead of treating every request as an isolated LLM call.

### Graph-Based Orchestration

LangGraph is used to represent the chatbot workflow as a state graph.

### Persistent Memory

SQLite checkpointing allows conversation state to persist beyond the lifetime of an individual Streamlit interaction.

### Thread-Based Conversations

Each conversation is identified using a unique `thread_id`, allowing multiple independent conversations.

### Streaming

LLM responses are streamed to the frontend for improved user experience.

### Separation of Frontend and Backend

The Streamlit UI communicates with a separate chatbot backend containing the LangGraph workflow.

---

# 📌 Current Limitations

The current implementation intentionally keeps the architecture simple.

It currently does **not** include:

- Authentication or user accounts
- RAG / document retrieval
- External tools
- Function/tool calling
- Agentic decision making
- Web search
- Conversation summarization
- Long-term user memory beyond persisted thread history
- Production database
- API layer such as FastAPI
- Automated evaluation
- LLM observability
- Rate limiting
- Production deployment configuration

These can be added as the application evolves.

---

# 🚀 Future Improvements

Potential extensions include:

### 1. RAG

Add document ingestion and retrieval:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
Retriever
    ↓
LangGraph
    ↓
Gemini
```

### 2. Tool Calling

Introduce tools such as:

- Web search
- Calculator
- Database queries
- APIs
- Custom business tools

### 3. Agentic Workflow

Extend the current single-node graph into a multi-node agent:

```text
User
 ↓
Planner
 ↓
Tool Selection
 ↓
Tool Execution
 ↓
Reflection
 ↓
Final Response
```

### 4. Production API

Separate the Streamlit frontend from the backend using FastAPI:

```text
Streamlit
    │
    ▼
FastAPI
    │
    ▼
LangGraph
    │
    ├── Gemini
    └── Database
```

### 5. Observability

Add LangSmith or another observability platform to track:

- Latency
- Token usage
- Errors
- Traces
- Model responses
- Conversation quality

### 6. Production Database

Replace SQLite with a production-grade database such as PostgreSQL when scaling to multiple users and concurrent workloads.

---

# 📈 Learning Outcomes

Through this project, the following concepts are explored:

- LangChain message abstractions
- LangGraph state management
- StateGraph
- Graph nodes and edges
- LangGraph checkpointing
- SQLite persistence
- Thread-based conversation management
- Streamlit session state
- LLM response streaming
- Gemini integration
- Stateful conversational AI architecture

---

## 👨‍💻 Author

**Ayush Singh**

Built as a practical implementation of a **stateful conversational AI application using LangGraph and Gemini**.