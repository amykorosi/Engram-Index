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

/* ── Sidebar ── */
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

/* ── Chat avatars ── */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #E8EEF0 !important;
    color: #00637C !important;
}

[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #00637C !important;
    color: #FFFFFF !important;
}

/* ── Kill red focus border on chat input ── */
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #00637C !important;
    box-shadow: 0 0 0 1px #00637C !important;
}

/* ── Action bar: LinkedIn link button ── */
.action-linkedin-btn {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    color: #00637C;
    padding: 7px 16px;
    border-radius: 8px;
    border: 1px solid #C8D8DB;
    background: white;
    transition: all 0.15s ease;
    gap: 3px;
}

.action-linkedin-btn:hover {
    background: rgba(0, 99, 124, 0.07);
    border-color: #00637C;
    text-decoration: none;
    color: #00637C;
}

.action-linkedin-icon {
    font-size: 13px;
    font-weight: 800;
    font-family: sans-serif;
    line-height: 1;
}

.action-linkedin-label {
    font-size: 10px;
    color: #7A6E61;
    line-height: 1;
}

/* ── Action bar: Download button ── */
[data-testid="stDownloadButton"] > button {
    background: white !important;
    color: #00637C !important;
    border: 1px solid #C8D8DB !important;
    border-radius: 8px !important;
    padding: 7px 16px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    min-height: unset !important;
    line-height: 1.6 !important;
    transition: all 0.15s ease !important;
    width: auto !important;
}

[data-testid="stDownloadButton"] > button:hover:not(:disabled) {
    background: rgba(0, 99, 124, 0.07) !important;
    border-color: #00637C !important;
}

[data-testid="stDownloadButton"] > button:disabled {
    color: #C4CDD1 !important;
    border-color: #E5EAEB !important;
    background: #F7F9FA !important;
    cursor: not-allowed !important;
}

</style>
""", unsafe_allow_html=True)


# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ── Sidebar ──
with st.sidebar:
    st.markdown('''
        <div style="display:flex; align-items:center; gap:12px; padding:6px 0 18px 0;">
            <div style="width:38px; height:38px; background:#1F3A4A; border-radius:10px;
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-size:18px; flex-shrink:0;">🗄️</div>
            <div>
                <div style="font-weight:700; font-size:15px; color:#1F2933; line-height:1.2;">Amy's Engram</div>
                <div style="font-size:11px; color:#7A6E61; margin-top:3px;">Structured professional memory</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.divider()
    for i, role in enumerate(ROLES):
        label = f"{role['title']}\n{role['company']}  ·  {role['dates']}"
        if st.button(label, key=f"role_{i}"):
            st.session_state.pending_prompt = ROLE_PROMPT.format(**role)
            st.session_state.pending_display = ROLE_DISPLAY.format(**role)
            st.rerun()


# ── Main header ──
st.markdown('''
    <div style="padding:8px 0 4px 0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:3px;">
            <span style="font-size:22px; color:#00637C; line-height:1;">✦</span>
            <span style="font-size:28px; font-weight:700; color:#1F2933;
                         letter-spacing:-0.5px; line-height:1;">Index</span>
        </div>
        <div style="font-size:10px; letter-spacing:0.18em; color:#7A6E61;
                    text-transform:uppercase; margin-bottom:14px; padding-left:2px;">
            Powered by Snowflake
        </div>
        <p style="font-size:14px; color:#4B5563; line-height:1.6; margin:0;">
            Index searches Amy's professional Engram: a structured knowledge base of
            career evidence, leadership philosophy, and references.
        </p>
    </div>
''', unsafe_allow_html=True)
st.divider()


# ── Messages ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ── Pending role prompt ──
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


# ── Action bar ──
st.markdown(
    '<hr style="border:none; border-top:1px solid #E5E7EB; margin:20px 0 12px 0;">',
    unsafe_allow_html=True
)

bar_col1, bar_col2, bar_col3 = st.columns([1.2, 1.5, 5])

with bar_col1:
    st.markdown('''
        <a href="https://www.linkedin.com/in/amy-korosi-1972b8b/"
           target="_blank" class="action-linkedin-btn">
            <span class="action-linkedin-icon">in</span>
            <span class="action-linkedin-label">Connect</span>
        </a>
    ''', unsafe_allow_html=True)

with bar_col2:
    has_conversation = any(m["role"] == "assistant" for m in st.session_state.messages)
    st.download_button(
        label="↓  Save Chat",
        data=build_conversation_markdown(),
        file_name="Amy_Korosi_Index_Conversation.md",
        mime="text/markdown",
        disabled=not has_conversation,
    )

with bar_col3:
    st.markdown(
        '<p style="font-size:12px; color:#9A8F80; padding-top:9px; font-style:italic;">'
        "Index searches Amy's professional Engram — ask anything.</p>",
        unsafe_allow_html=True
    )


# ── Chat input ──
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
