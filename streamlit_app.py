import streamlit as st
import requests
import uuid

st.set_page_config(
    page_title="Ask Index About Amy Korosi",
    page_icon="✦",
    layout="centered"
)

ACCOUNT_URL = "https://cnnqtpa-am36229.snowflakecomputing.com"
API_ENDPOINT = f"{ACCOUNT_URL}/api/v2/databases/ENGRAM/schemas/AGENTS/agents/INDEX:run"
SQL_ENDPOINT = f"{ACCOUNT_URL}/api/v2/statements"

ROLES = [
    {"title": "SVP, Data, Technology & Operations", "company": "Globalfaces Direct", "dates": "2023-Present"},
    {"title": "VP, Analytics & Automation", "company": "Hudson's Bay Company", "dates": "2021-2023"},
    {"title": "DVP, Analytics Enablement", "company": "Hudson's Bay Company", "dates": "2020"},
    {"title": "Director, Digital Product Delivery", "company": "CIBC", "dates": "2018-2019"},
    {"title": "Head of Product", "company": "Juice Mobile AdTech", "dates": "2017-2018"},
    {"title": "Director, Product & Analytics", "company": "Rogers Communications", "dates": "2013-2017"},
    {"title": "Sr. Manager, Strategy & Analytics", "company": "Rogers Communications", "dates": "2010-2012"},
    {"title": "Analytics Foundations", "company": "Klick, Wunderman, Foresters, Enbridge", "dates": "2000-2010"},
    {"title": "Geographic Information Systems", "company": "Algonquin College", "dates": "1997-2000"},
]

ROLE_PROMPT = (
    "Give me a brief overview of what Amy did as {title} at {company} from {dates}, "
    "then list the specific projects with a brief description from that role "
    "so I can choose what to explore further."
)

ROLE_DISPLAY = "Tell me about Amy's time as {title} at {company} ({dates})"

def call_index_agent(messages):
    pat = st.secrets["snowflake"]["pat"]
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
    }
    body = {"messages": messages, "stream": False}
    response = requests.post(API_ENDPOINT, json=body, headers=headers)
    if response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"
    try:
        data = response.json()
        content_blocks = data.get("content", [])
        text_parts = [
            block["text"]
            for block in content_blocks
            if block.get("type") == "text" and block.get("text", "").strip()
        ]
        return " ".join(text_parts).strip()
    except Exception as e:
        return f"Parse error: {str(e)} -- Raw: {response.text[:500]}"

def log_to_snowflake(session_id, role, content):
    try:
        pat = st.secrets["snowflake"]["pat"]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {pat}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "User-Agent": "EngramApp/1.0",
        }
        body = {
            "statement": "INSERT INTO ENGRAM.AGENTS.INDEX_CONVERSATIONS (session_id, role, message_content) VALUES (?, ?, ?)",
            "timeout": 60,
            "warehouse": "ENGRAM_WH",
            "database": "ENGRAM",
            "schema": "AGENTS",
            "bindings": {
                "1": {"type": "TEXT", "value": session_id},
                "2": {"type": "TEXT", "value": role},
                "3": {"type": "TEXT", "value": content},
            },
        }
        requests.post(SQL_ENDPOINT, json=body, headers=headers)
    except:
        pass

def build_conversation_markdown():
    lines = [
        "# Index Conversation -- Amy Korosi",
        "",
        "Index is Amy Korosi's professional engram: a structured knowledge base of career evidence, leadership philosophy, and references. This document is a record of a conversation that took place with Index.",
        "",
        "To continue this conversation: https://engram-index.streamlit.app/",
        "",
        "---",
        ""
    ]
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lines.append(f"**Question:** {msg['content']}")
            lines.append("")
        else:
            lines.append(f"**Index:** {msg['content']}")
            lines.append("")
    return "\n".join(lines)

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    border-left: 3px solid #00637C;
    border-radius: 0 6px 6px 0;
    text-align: left;
    padding: 10px 10px 10px 14px;
    color: #31333F;
    width: 100%;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 4px;
    white-space: normal;
    transition: all 0.15s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0, 99, 124, 0.07);
    color: #00637C;
    border-left-color: #00637C;
}

[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background: rgba(0, 99, 124, 0.12);
    color: #00637C;
    border-left-color: #00637C;
    box-shadow: none;
    outline: none;
}

[data-testid="stSidebar"] strong {
    color: #00637C;
}

[data-testid="stChatMessageAvatarUser"] {
    background-color: #E8EEF0 !important;
    color: #00637C !important;
}

[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #00637C !important;
    color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

with st.sidebar:
    st.markdown("**Career Engram**")
    st.divider()
    for i, role in enumerate(ROLES):
        label = f"{role['title']}\n{role['company']}  ·  {role['dates']}"
        if st.button(label, key=f"role_{i}"):
            st.session_state.pending_prompt = ROLE_PROMPT.format(**role)
            st.session_state.pending_display = ROLE_DISPLAY.format(**role)
            st.rerun()

st.title("Ask Index About Amy Korosi")
st.markdown("Index searches Amy's professional Engram: a structured knowledge base of career evidence, leadership philosophy, and references.")
st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "pending_prompt" in st.session_state:
    actual_prompt = st.session_state.pop("pending_prompt")
    display_text = st.session_state.pop("pending_display", actual_prompt)

    st.session_state.messages.append({"role": "user", "content": display_text})
    log_to_snowflake(st.session_state.session_id, "user", display_text)

    with st.chat_message("user"):
        st.markdown(display_text)

    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages[:-1]
    ] + [{"role": "user", "content": [{"type": "text", "text": actual_prompt}]}]

    with st.chat_message("assistant"):
        with st.spinner("Index is searching..."):
            response_text = call_index_agent(api_messages)
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    log_to_snowflake(st.session_state.session_id, "assistant", response_text)
    st.rerun()

if prompt := st.chat_input("Ask anything about Amy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    log_to_snowflake(st.session_state.session_id, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages
    ]
    with st.chat_message("assistant"):
        with st.spinner("Index is searching..."):
            response_text = call_index_agent(api_messages)
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    log_to_snowflake(st.session_state.session_id, "assistant", response_text)

st.divider()
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(
        "Connect with Amy on [LinkedIn](https://www.linkedin.com/in/amy-korosi-1972b8b/)",
        unsafe_allow_html=True
    )

with col2:
    has_conversation = any(m["role"] == "assistant" for m in st.session_state.messages)
    st.download_button(
        label="Download Conversation",
        data=build_conversation_markdown(),
        file_name="Amy_Korosi_Index_Conversation.md",
        mime="text/markdown",
        disabled=not has_conversation
    )
