import streamlit as st
import requests
import uuid
from datetime import datetime


# ============================================================
# Page config
# ============================================================

st.set_page_config(
    page_title="Ask Index About Amy Korosi",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Snowflake config
# ============================================================

ACCOUNT_URL = "https://cnnqtpa-am36229.snowflakecomputing.com"
API_ENDPOINT = f"{ACCOUNT_URL}/api/v2/databases/ENGRAM/schemas/AGENTS/agents/INDEX:run"
SQL_ENDPOINT = f"{ACCOUNT_URL}/api/v2/statements"

LINKEDIN_URL = "https://www.linkedin.com/in/amy-korosi-1972b8b/"
APP_URL = "https://engram-index.streamlit.app/"


# ============================================================
# Sidebar role history
# ============================================================

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


STARTER_QUESTIONS = [
    {
        "label": "Tell me about Amy",
        "prompt": "Tell me about Amy. Start with a concise professional overview, then give me the most important things to know."
    },
    {
        "label": "Why Snowflake?",
        "prompt": "Why does Amy want to work at Snowflake, and what would Amy bring to Snowflake?"
    },
    {
        "label": "How was Index built?",
        "prompt": "How was Engram and Index built? Explain the process, architecture, and what the prototype demonstrates."
    },
    {
        "label": "What has Amy built on Snowflake?",
        "prompt": "What has Amy built on Snowflake? Include specific examples and what they show about Amy's approach."
    },
]


# ============================================================
# Helpers
# ============================================================

def get_pat():
    try:
        return st.secrets["snowflake"]["pat"]
    except Exception:
        return None


def call_index_agent(messages):
    pat = get_pat()
    if not pat:
        return (
            "Index is missing the Snowflake programmatic access token. "
            "Add it to Streamlit secrets under [snowflake] with the key pat."
        )

    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    }

    body = {"messages": messages, "stream": False}

    try:
        response = requests.post(API_ENDPOINT, json=body, headers=headers, timeout=60)
    except requests.RequestException as e:
        return f"Index could not reach Snowflake. Error: {str(e)}"

    if response.status_code != 200:
        return f"Snowflake returned Error {response.status_code}: {response.text}"

    try:
        data = response.json()
        content_blocks = data.get("content", [])

        text_parts = []
        for block in content_blocks:
            if block.get("type") == "text" and block.get("text", "").strip():
                text_parts.append(block["text"])

        if text_parts:
            return "\n\n".join(text_parts).strip()

        return "Index returned a response, but no text content was found."

    except Exception as e:
        return f"Index returned a response, but it could not be parsed. Error: {str(e)}. Raw: {response.text[:500]}"


def log_to_snowflake(session_id, role, content):
    pat = get_pat()
    if not pat:
        return

    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {pat}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "User-Agent": "EngramApp/1.0",
        }

        body = {
            "statement": (
                "INSERT INTO ENGRAM.AGENTS.INDEX_CONVERSATIONS "
                "(session_id, role, message_content) VALUES (?, ?, ?)"
            ),
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

        requests.post(SQL_ENDPOINT, json=body, headers=headers, timeout=15)

    except Exception:
        pass


def build_api_messages(latest_prompt=None):
    api_messages = [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages
    ]

    if latest_prompt:
        api_messages.append(
            {"role": "user", "content": [{"type": "text", "text": latest_prompt}]}
        )

    return api_messages


def build_conversation_markdown():
    lines = [
        "# Index Conversation - Amy Korosi",
        "",
        "Index is Amy Korosi's professional Engram: a structured knowledge base of career evidence, leadership philosophy, and references.",
        "",
        f"Conversation exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"Continue the conversation: {APP_URL}",
        "",
        "---",
        "",
    ]

    if not st.session_state.messages:
        lines.append("No conversation has been started yet.")
        return "\n".join(lines)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            lines.append(f"## Question")
            lines.append(msg["content"])
            lines.append("")
        else:
            lines.append(f"## Index")
            lines.append(msg["content"])
            lines.append("")

    return "\n".join(lines)


def ask_index(actual_prompt, display_text=None):
    display_text = display_text or actual_prompt

    st.session_state.messages.append({"role": "user", "content": display_text})
    log_to_snowflake(st.session_state.session_id, "user", display_text)

    api_messages = build_api_messages()

    with st.spinner("Index is searching..."):
        response_text = call_index_agent(api_messages)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    log_to_snowflake(st.session_state.session_id, "assistant", response_text)

    st.rerun()


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
:root {
    --primary-dark: #22323D;
    --muted-teal: #2F6173;
    --soft-teal: #EAF1F3;
    --border: #DDE4E7;
    --border-soft: #E8EEF0;
    --text: #1F2933;
    --muted: #6B7280;
    --warm-muted: #8A8178;
    --soft-bg: #F7F9FA;
}

/* Page shell */
.stApp {
    background: #FFFFFF;
}

.block-container {
    padding-top: 3.25rem !important;
    padding-bottom: 2rem !important;
    max-width: 1220px;
}

/* Hide the default Streamlit top gap feeling */
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid var(--border-soft);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 2rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 4px 4px 22px 4px;
}

.sidebar-icon {
    width: 48px;
    height: 48px;
    background: var(--primary-dark);
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.sidebar-title {
    font-weight: 750;
    font-size: 17px;
    color: var(--text);
    line-height: 1.2;
    letter-spacing: -0.2px;
}

.sidebar-subtitle {
    font-size: 12px;
    color: var(--warm-muted);
    margin-top: 4px;
    font-weight: 400;
}

/* Sidebar role buttons */
[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: none;
    border-left: 3px solid var(--muted-teal);
    border-radius: 0 8px 8px 0;
    text-align: left;
    padding: 9px 10px 9px 14px;
    color: #31333F;
    width: 100%;
    font-size: 12.5px;
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: 6px;
    white-space: normal;
    transition: all 0.15s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(47, 97, 115, 0.07);
    color: var(--muted-teal);
    border-left-color: var(--muted-teal);
}

[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background: rgba(47, 97, 115, 0.12);
    color: var(--muted-teal);
    border-left-color: var(--muted-teal);
    box-shadow: none;
    outline: none;
}

/* Header */
.index-header {
    padding: 10px 0 20px 0;
}

.index-logo-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 3px;
}

.index-star {
    font-size: 22px;
    color: var(--muted-teal);
    line-height: 1.2;
}

.index-title {
    font-size: 32px;
    font-weight: 750;
    color: var(--text);
    letter-spacing: -0.6px;
    line-height: 1.2;
}

.index-powered {
    font-size: 10px;
    letter-spacing: 0.22em;
    color: var(--warm-muted);
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-left: 2px;
}

.index-intro {
    font-size: 14.5px;
    color: #4B5563;
    line-height: 1.65;
    max-width: 820px;
    margin: 0;
}

/* Starter prompts */
.starter-wrap {
    margin: 12px 0 18px 0;
    padding: 13px 14px;
    background: #FFFFFF;
    border: 1px solid var(--border-soft);
    border-radius: 14px;
}

.starter-label {
    font-size: 12px;
    font-weight: 750;
    color: var(--primary-dark);
    margin-bottom: 8px;
}

/* Main button style for starter question buttons */
div[data-testid="stButton"] > button {
    border-radius: 999px;
    border: 1px solid var(--border);
    background: #FFFFFF;
    color: var(--primary-dark);
    font-size: 12.5px;
    font-weight: 650;
    min-height: 36px;
}

div[data-testid="stButton"] > button:hover {
    border-color: var(--muted-teal);
    color: var(--muted-teal);
    background: rgba(47, 97, 115, 0.05);
}

/* Chat card */
.chat-card {
    border: 1px solid var(--border);
    border-radius: 16px;
    background: #FFFFFF;
    padding: 14px 16px 10px 16px;
    margin-top: 8px;
}

.chat-card-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: var(--primary-dark);
    font-size: 13px;
    font-weight: 750;
    margin-bottom: 10px;
}

.grounded-pill {
    font-size: 11px;
    color: var(--muted-teal);
    background: var(--soft-teal);
    border: 1px solid #D7E4E8;
    padding: 4px 9px;
    border-radius: 999px;
    font-weight: 650;
}

/* Empty chat state */
.empty-state {
    height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 9px;
    color: var(--muted);
    text-align: center;
    padding: 0 28px;
}

.empty-title {
    font-size: 18px;
    font-weight: 750;
    color: var(--primary-dark);
}

.empty-copy {
    font-size: 13px;
    max-width: 520px;
    line-height: 1.65;
    color: var(--muted);
}

/* Streamlit bordered container cleanup */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 16px !important;
}

/* Chat avatars */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #E8EEF0 !important;
    color: var(--muted-teal) !important;
}

[data-testid="stChatMessageAvatarAssistant"] {
    background-color: var(--muted-teal) !important;
    color: #FFFFFF !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent;
    padding: 0.35rem 0;
}

/* Chat input */
[data-testid="stChatInputContainer"] {
    border-color: var(--border) !important;
    background: #F4F6F8 !important;
    box-shadow: none !important;
    border-radius: 14px !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: var(--muted-teal) !important;
    box-shadow: 0 0 0 1px var(--muted-teal) !important;
}

div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="input"]:focus-within {
    border-color: var(--muted-teal) !important;
    box-shadow: none !important;
}

textarea:focus {
    outline: none !important;
    box-shadow: none !important;
}

/* Footer button area */
.footer-actions {
    margin-top: 16px;
}

.footer-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    width: 100%;
    height: 42px;
    padding: 0 15px;
    border: 1.25px solid var(--muted-teal);
    border-radius: 10px;
    background: white;
    color: var(--primary-dark);
    font-size: 13.5px;
    font-weight: 700;
    text-decoration: none !important;
    transition: all 0.15s ease;
    box-sizing: border-box;
    cursor: pointer;
}

.footer-btn:hover {
    background: rgba(47, 97, 115, 0.05);
    text-decoration: none !important;
    color: var(--primary-dark);
}

.linkedin-mark {
    color: #0A66C2;
    font-weight: 900;
    font-size: 15px;
    font-family: sans-serif;
    line-height: 1;
    flex-shrink: 0;
}

[data-testid="stDownloadButton"] {
    width: 100%;
}

[data-testid="stDownloadButton"] > button {
    width: 100% !important;
    height: 42px !important;
    padding: 0 15px !important;
    border: 1.25px solid var(--muted-teal) !important;
    border-radius: 10px !important;
    background: white !important;
    color: var(--primary-dark) !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    transition: all 0.15s ease !important;
    line-height: 1 !important;
}

[data-testid="stDownloadButton"] > button:hover:not(:disabled) {
    background: rgba(47, 97, 115, 0.05) !important;
    border-color: var(--muted-teal) !important;
    color: var(--primary-dark) !important;
}

[data-testid="stDownloadButton"] > button:disabled {
    color: #C4CDD1 !important;
    border-color: #E5EAEB !important;
    background: #F7F9FA !important;
    cursor: not-allowed !important;
}

.disclaimer {
    text-align: center;
    font-size: 11px;
    color: var(--warm-muted);
    font-style: italic;
    margin-top: 13px;
    padding: 0 8px;
    line-height: 1.55;
}

/* Make mobile less awkward */
@media (max-width: 768px) {
    .block-container {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .index-title {
        font-size: 28px;
    }

    .empty-state {
        height: 220px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# Session state
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                     stroke-width="1.5" stroke="white" width="25" height="25">
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
                <div class="sidebar-title">Amy's Engram</div>
                <div class="sidebar-subtitle">Structured professional memory</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    for i, role in enumerate(ROLES):
        label = f"{role['title']}\n{role['company']}  ·  {role['dates']}"
        if st.button(label, key=f"role_{i}", use_container_width=True):
            st.session_state.pending_prompt = ROLE_PROMPT.format(**role)
            st.session_state.pending_display = ROLE_DISPLAY.format(**role)
            st.rerun()


# ============================================================
# Main layout
# ============================================================

left_spacer, main_col, right_spacer = st.columns([0.08, 0.84, 0.08])

with main_col:
    # Header
    st.markdown(
        """
        <div class="index-header">
            <div class="index-logo-row">
                <span class="index-star">✦</span>
                <span class="index-title">Index</span>
            </div>
            <div class="index-powered">Powered by Snowflake</div>
            <p class="index-intro">
                Index searches Amy's professional Engram: a structured knowledge base of career evidence,
                leadership philosophy, and references.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Starter prompts only before a conversation starts
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="starter-wrap">
                <div class="starter-label">Try asking:</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        starter_cols = st.columns(4)
        for i, item in enumerate(STARTER_QUESTIONS):
            with starter_cols[i]:
                if st.button(item["label"], key=f"starter_{i}", use_container_width=True):
                    st.session_state.pending_prompt = item["prompt"]
                    st.session_state.pending_display = item["label"]
                    st.rerun()

    # Chat frame
    st.markdown(
        """
        <div class="chat-card-title">
            <span>Chat with Index</span>
            <span class="grounded-pill">Grounded retrieval</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        message_area = st.container(height=360)

        with message_area:
            if not st.session_state.messages:
                st.markdown(
                    """
                    <div class="empty-state">
                        <div class="empty-title">Ask Index about Amy</div>
                        <div class="empty-copy">
                            Ask about Amy's work, Snowflake experience, leadership style,
                            references, or how Engram and Index were built.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            for message in st.session_state.messages:
                avatar = "👤" if message["role"] == "user" else "✦"
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        prompt = st.chat_input("Ask anything about Amy...")

    # Handle pending starter or role prompt
    if "pending_prompt" in st.session_state:
        actual_prompt = st.session_state.pop("pending_prompt")
        display_text = st.session_state.pop("pending_display", actual_prompt)
        ask_index(actual_prompt=actual_prompt, display_text=display_text)

    # Handle direct chat prompt
    if prompt:
        ask_index(actual_prompt=prompt, display_text=prompt)

    # Footer actions
    has_conversation = any(m["role"] == "assistant" for m in st.session_state.messages)

    st.markdown('<div class="footer-actions"></div>', unsafe_allow_html=True)

    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1.25])

    with footer_col1:
        st.markdown(
            f"""
            <a href="{LINKEDIN_URL}"
               target="_blank"
               class="footer-btn">
                <span class="linkedin-mark">in</span>
                Connect on LinkedIn
            </a>
            """,
            unsafe_allow_html=True,
        )

    with footer_col2:
        st.download_button(
            label="↓  Download Summary",
            data=build_conversation_markdown(),
            file_name="Amy_Korosi_Index_Conversation.md",
            mime="text/markdown",
            disabled=not has_conversation,
            use_container_width=True,
        )

    with footer_col3:
        st.empty()

    st.markdown(
        """
        <p class="disclaimer">
            Prototype disclosure: Index began May 16, 2026 and is a work in progress.
            Feedback is welcome via LinkedIn.
        </p>
        """,
        unsafe_allow_html=True,
    )
