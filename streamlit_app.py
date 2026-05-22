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

/* ── Pull page top padding up ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}

/* ── Sidebar base ── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* ── Sidebar role buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    border-left: 3px solid #00637C;
    border-radius: 0 6px 6px 0;
    text-align: left;
    padding: 9px 10px 9px 14px;
    color: #31333F;
    width: 100%;
    font-size: 12.5px;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 3px;
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

/* ── Kill red border on chat input everywhere ── */
[data-testid="stChatInputContainer"] {
    border-color: #D1D9DB !important;
    box-shadow: none !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: #00637C !important;
    box-shadow: 0 0 0 1px #00637C !important;
}

div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="input"]:focus-within {
    border-color: #00637C !important;
    box-shadow: none !important;
}

textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* ── Footer button columns equal width ── */
div[data-testid="column"] {
    padding-left: 4px !important;
    padding-right: 4px !important;
}

/* ── LinkedIn anchor button ── */
.footer-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    height: 48px;
    padding: 0 16px;
    border: 1.5px solid #00637C;
    border-radius: 8px;
    background: white;
    color: #1F2933;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none !important;
    transition: all 0.15s ease;
    box-sizing: border-box;
    cursor: pointer;
}

.footer-btn:hover {
    background: rgba(0, 99, 124, 0.05);
    text-decoration: none !important;
    color: #1F2933;
}

.linkedin-mark {
    color: #0A66C2;
    font-weight: 900;
    font-size: 15px;
    font-family: sans-serif;
    line-height: 1;
    flex-shrink: 0;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] {
    width: 100%;
}

[data-testid="stDownloadButton"] > button {
    width: 100% !important;
    height: 48px !important;
    padding: 0 16px !important;
    border: 1.5px solid #00637C !important;
    border-radius: 8px !important;
    background: white !important;
    color: #1F2933 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
    line-height: 1 !important;
}

[data-testid="stDownloadButton"] > button:hover:not(:disabled) {
    background: rgba(0, 99, 124, 0.05) !important;
    border-color: #00637C !important;
    color: #1F2933 !important;
}

[data-testid="stDownloadButton"] > button:disabled {
    color: #C4CDD1 !important;
    border-color: #E5EAEB !important;
    background: #F7F9FA !important;
    cursor: not-allowed !important;
}

/* ── Disclaimer ── */
.disclaimer {
    text-align: center;
    font-size: 11.5px;
    color: #9A8F80;
    font-style: italic;
    margin-top: 14px;
    padding: 0 8px;
    line-height: 1.7;
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
        <div style="
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 4px 4px 22px 4px;
        ">
            <div style="
                width: 48px;
                height: 48px;
                background: #1F3A4A;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            ">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                     stroke-width="1.5" stroke="white" width="24" height="24">
                  <path stroke-linecap="round" stroke-linejoin="round"
                    d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5
                    0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0
                    2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5
                    0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12
                    18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25
                    4.125s-8.25-1.847-8.25-4.125" />
                </svg>
            </div>
            <div>
                <div style="
                    font-weight: 700;
                    font-size: 17px;
                    color: #1F2933;
                    line-height: 1.2;
                    letter-spacing: -0.2px;
                ">Amy's Engram</div>
                <div style="
                    font-size: 12px;
                    color: #7A6E61;
                    margin-top: 4px;
                    font-weight: 400;
                ">Structured professional memory</div>
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
    <div style="padding: 0 0 10px 0;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
            <span style="font-size: 22px; color: #00637C; line-height: 1;">✦</span>
            <span style="
                font-size: 30px;
                font-weight: 700;
                color: #1F2933;
                letter-spacing: -0.5px;
                line-height: 1;
            ">Index</span>
        </div>
        <div style="
            font-size: 10px;
            letter-spacing: 0.2em;
            color: #7A6E61;
            text-transform: uppercase;
            margin-bottom: 12px;
            padding-left: 2px;
        ">Powered by Snowflake</div>
        <p style="
            font-size: 14px;
            color: #4B5563;
            line-height: 1.65;
            margin: 0;
        ">
            Index searches Amy's professional Engram: a structured knowledge base of
            career evidence, leadership philosophy, and references.
        </p>
    </div>
''', unsafe_allow_html=True)


# ── Chat frame ──
with st.container(border=True):
    message_area = st.container(height=340)
    with message_area:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    prompt = st.chat_input("Ask anything about Amy...")


# ── Handle pending role prompt ──
if "pending_prompt" in st.session_state:
    actual_prompt = st.session_state.pop("pending_prompt")
    display_text = st.session_state.pop("pending_display", actual_prompt)

    st.session_state.messages.append({"role": "user", "content": display_text})
    log_to_snowflake(st.session_state.session_id, "user", display_text)

    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages[:-1]
    ] + [{"role": "user", "content": [{"type": "text", "text": actual_prompt}]}]

    with st.spinner("Index is searching..."):
        response_text = call_index_agent(api_messages)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    log_to_snowflake(st.session_state.session_id, "assistant", response_text)
    st.rerun()


# ── Handle direct prompt ──
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    log_to_snowflake(st.session_state.session_id, "user", prompt)

    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages
    ]

    with st.spinner("Index is searching..."):
        response_text = call_index_agent(api_messages)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    log_to_snowflake(st.session_state.session_id, "assistant", response_text)
    st.rerun()


# ── Footer buttons ──
has_conversation = any(m["role"] == "assistant" for m in st.session_state.messages)

col1, col2 = st.columns(2)

with col1:
    st.markdown('''
        <a href="https://www.linkedin.com/in/amy-korosi-1972b8b/"
           target="_blank"
           class="footer-btn">
            <span class="linkedin-mark">in</span>
            Connect on LinkedIn
        </a>
    ''', unsafe_allow_html=True)

with col2:
    st.download_button(
        label="↓  Download Summary",
        data=build_conversation_markdown(),
        file_name="Amy_Korosi_Index_Conversation.md",
        mime="text/markdown",
        disabled=not has_conversation,
    )

# ── Disclaimer ──
st.markdown(
    '<p class="disclaimer">This prototype began May 16th 2026, it is a work in progress. '
    'Please feel free to reach out to Amy via LinkedIn if you have any feedback.</p>',
    unsafe_allow_html=True
)
