import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Ask Index About Amy Korosi",
    page_icon="✦",
    layout="centered"
)

ACCOUNT_URL = "https://cnnqtpa-am36229.snowflakecomputing.com"
AGENT_PATH = "ENGRAM.AGENTS.INDEX"
API_ENDPOINT = f"{ACCOUNT_URL}/api/v2/cortex/agent:run"

STARTER_QUESTIONS = [
    "Tell me about Amy Korosi",
    "What is the coolest thing Amy has built?",
    "What is unique about Amy?",
    "What do people have to say about Amy?",
    "What patterns do you see in Amy's history?",
    "What even is this application?"
]

def call_index_agent(messages):
    pat = st.secrets["snowflake"]["pat"]
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
    }
    body = {
        "agent": AGENT_PATH,
        "messages": messages,
        "stream": False
    }
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

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Ask Index About Amy Korosi")
st.markdown("Index searches Amy's professional Engram: a structured knowledge base of career evidence, leadership philosophy, and references.")
st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    st.markdown("**Some questions to get you started:**")
    cols = st.columns(2)
    for i, question in enumerate(STARTER_QUESTIONS):
        if cols[i % 2].button(question, key=f"starter_{i}"):
            st.session_state.pending_question = question
            st.rerun()

if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
    st.session_state.messages.append({"role": "user", "content": prompt})
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
    st.rerun()

if prompt := st.chat_input("Ask anything about Amy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
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

st.divider()
st.caption("This is a week-old idea and prototype, still a work in progress. Feedback is very much appreciated.")
