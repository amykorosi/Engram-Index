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

def call_index_agent(question):
    pat = st.secrets["snowflake"]["pat"]
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN"
    }
    body = {
        "agent": AGENT_PATH,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": question}]
            }
        ],
        "stream": False
    }
    response = requests.post(API_ENDPOINT, json=body, headers=headers)
    return response.status_code, response.text

st.title("Ask Index About Amy Korosi -- Debug Mode")

question = st.text_input("Ask something:")
if st.button("Send"):
    with st.spinner("Calling agent..."):
        status, raw = call_index_agent(question)
    st.write(f"Status: {status}")
    st.code(raw[:3000])
