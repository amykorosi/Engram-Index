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
    "Tell me about Amy",
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
        "Accept": "text/event-stream",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
    }
    body = {
        "agent": AGENT_PATH,
        "messages": messages,
        "stream": True
    }
    response = requests.post(API_ENDPOINT, json=body, headers=headers, stream=True)
    
    if response.status_code != 200:
        yield f"Error {response.status_code}: {response.text}"
        return

    current_event = None
    full_raw = []
    
    for line in response.iter_lines():
        if not line:
            continue
        line = line.decode("utf-8")
        full_raw.append(line)
        if line.startswith("event:"):
            current_event = line[6:].strip()
        elif line.startswith("data:"):
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                break
            if current_event == "response.text.delta":
                try:
                    data = json.loads(data_str)
                    delta = data.get("delta", {}).get("text", "")
                    if delta:
                        yield delta
                except json.JSONDecodeError:
                    pass

    if not any("response.text.delta" in r for r in full_raw):
        events_seen = [r for r in full_raw if r.startswith("event:")]
        yield f"No text response received. Events seen: {events_seen[:10]}"

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
        response_text = st.write_stream(call_index_agent(api_messages))
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
        response_text = st.write_stream(call_index_agent(api_messages))
    st.session_state.messages.append({"role": "assistant", "content": response_text})

st.divider()
st.caption("This is a week-old idea and prototype, still a work in progress. Feedback is very much appreciated.")
