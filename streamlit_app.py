import streamlit as st
import requests

st.set_page_config(
    page_title="Ask Index About Amy Korosi",
    page_icon="✦",
    layout="centered"
)

ACCOUNT_URL = "https://cnnqtpa-am36229.snowflakecomputing.com"
API_ENDPOINT = f"{ACCOUNT_URL}/api/v2/databases/ENGRAM/schemas/AGENTS/agents/INDEX:run"

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

# ── CSS: sidebar button styling ──
st.markdown("""
<style>
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    border-left: 3px solid #00637C;
    border-radius: 0 6px 6px 0;
    text-align: left;
    padding: 8px 10px 8px 14px;
    color: #31333F;
    width: 100%;
    font-size: 12px;
    line-height: 1.35;
    margin-bottom: 2px;
    white-space: normal;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0, 99, 124, 0.08);
    border-left-color: #00637C;
    color: #00637C;
}
[data-testid="stSidebar"] .stButton > button:active,
[data-testid="stSidebar"] .stButton > button:focus {
    background: rgba(0, 99, 124, 0.14);
    border-left-color: #00637C;
    color: #00637C;
    outline: none;
    box-shadow: none;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ──
with st.sidebar:
    st.markdown("**Career Engram**")
    st.divider()
    for i, role in enumerate(ROLES):
        label = f"{role['title']}\n{role['company']}  ·  {role['dates']}"
        if st.button(label, key=f"role_{i}"):
            st.session_state.pending_prompt = ROLE_PROMPT.format(**role)
            st.session_state.pending_display = ROLE_DISPLAY.format(**role)
            st.rerun()

# ── Header ──
st.title("Ask Index About Amy Korosi")
st.markdown("Index searches Amy's professional Engram: a structured knowledge base of career evidence, leadership philosophy, and references.")
st.divider()

# ── Chat history ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Pending question handler ──
if "pending_prompt" in st.session_state:
    actual_prompt = st.session_state.pop("pending_prompt")
    display_text = st.session_state.pop("pending_display", actual_prompt)

    st.session_state.messages.append({"role": "user", "content": display_text})
    with st.chat_message("user"):
        st.markdown(display_text)

    # Send actual structured prompt to Index, not the display text
    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages[:-1]
    ] + [{"role": "user", "content": [{"type": "text", "text": actual_prompt}]}]

    with st.chat_message("assistant"):
        with st.spinner("Index is searching..."):
            response_text = call_index_agent(api_messages)
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.rerun()

# ── Chat input ──
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
