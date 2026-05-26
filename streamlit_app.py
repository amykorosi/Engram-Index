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
    {"title": "DVP, Analytics Enablement", "company": "Hudson's Bay Company", "dates": "2020-2021"},
    {"title": "Director, Digital Product Delivery", "company": "CIBC", "dates": "2019"},
    {"title": "Head of Product", "company": "Juice Mobile AdTech", "dates": "2017-2018"},
    {"title": "Director, Product & Analytics", "company": "Rogers Communications", "dates": "2013-2016"},
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


# ============================================================
# Questions content
# ============================================================

QUESTIONS = {
    "Leadership": [
        "How does Amy build high performing teams?",
        "Is Amy comfortable speaking in front of crowds?",
        "How does she keep her teams up to date?",
        "How does Amy communicate data strategy to executives who are not data people?",
        "How has Amy built data culture inside an organization?",
    ],
    "Experience": [
        "Give me examples of strategy to execution work Amy has done",
        "What AI products has Amy built?",
        "What Snowflake experience does Amy have?",
        "How is Amy both a data and a product person?",
    ],
    "References": [
        "List Amy's references with job titles and a brief summary of what is in each note",
        "What patterns are in Amy's references?",
        "How does Amy's work experience align with what her references say?",
    ],
    "Just for Fun": [
        "What is Amy's special?",
        "What does Amy do outside of work?",
        "What does Amy not know about herself?",
        "What is the coolest thing Amy has built?",
        "What does Amy think food and data have in common?",
        "What would surprise people most about Amy's career path?",
        "Why and how was this application built?",
        "What does Amy do next with Engram and Index?",
    ],
}


# ============================================================
# Resume content
# ============================================================

RESUME = [
    {
        "title": "SVP, Data & Technology",
        "company": "Globalfaces Direct",
        "dates": "2023 to Present",
        "summary": "Lead Data, Technology, Privacy, and Call Center Operations for Globalfaces Direct, a high-volume North American fundraising business supporting 70+ charity brands. Work spans data strategy and execution, platform modernization, operational infrastructure, governance, and AI-native capability built directly on Snowflake.",
        "bullets": [
            "Built a modern data ecosystem using Snowflake, Sigma, Fivetran, and Azure to improve reporting, visibility, and executive decision-making across the business",
            "Led digital product modernization including the rebuild of the field tablet application deployed to 1,000+ tablets and development of Office in the Box as a scalable platform for standardized office operations",
            "Automated invoicing for 70+ charities and payroll for 800 fundraisers, reducing manual effort and improving accuracy",
            "Built PULSE, a Snowflake-native AI operations intelligence platform using Cortex Agents, Cortex Search, and Streamlit to make business knowledge accessible through natural language",
            "Launched near real-time fraud detection and a CIT Command Center to improve donor data integrity and field operational oversight",
        ],
    },
    {
        "title": "VP, Analytics & Automation",
        "company": "Hudson's Bay Company",
        "dates": "2021 to 2023",
        "summary": "Led analytics, machine learning, automation, and data enablement for Hudson's Bay and TheBay.com during a period of major retail and digital transformation. Reported to the CFO, led a team of 20, and focused on building a more connected analytics operating model that improved trust in the numbers and connected data to business decisions.",
        "bullets": [
            "Built a hub-and-spoke analytics operating model that clarified ownership, improved cross-functional alignment, and made analytics easier for executives and business partners to act on",
            "Led profitability analytics that moved the business from broad assumptions to product-level economics, helping Finance and Merchandising understand margin, fulfillment costs, returns, and online assortment decisions",
            "Advanced ML and automation use cases including NLP for website metadata, competitive price intelligence, call center demand forecasting, and returns planning",
            "Built an in-house price scraping capability enabling daily price updates and eliminating thousands of hours of manual work",
            "Founded and led the Data Culture Committee, delivering datathons, training programs, and monthly executive sessions",
        ],
    },
    {
        "title": "DVP, Analytics Enablement",
        "company": "Hudson's Bay Company",
        "dates": "2020 to 2021",
        "summary": "Led modernization of the enterprise BI environment across Hudson's Bay, Saks Fifth Avenue, and Saks OFF 5TH. Treated business intelligence as a product: structure, roadmaps, rollout plans, governance, and user experiences that made reporting more trusted, actionable, and easier for leaders to use.",
        "bullets": [
            "Led Snowflake migration and BI consolidation, sunsetting a 10-year-old legacy data environment across 2,000 users and three retail banners",
            "Introduced Dataiku for data science and ML enablement across the organization",
            "Launched mobile executive KPI dashboards improving visibility and reducing reliance on static reporting",
            "Built employee fraud detection capability at Saks Fifth Avenue combining transaction pattern analysis with exception-based alerting",
            "Created monthly executive steering committees and bi-weekly stakeholder forums to align marketing, supply chain, and planning teams",
        ],
    },
    {
        "title": "Director, Digital Product Delivery",
        "company": "CIBC",
        "dates": "2019",
        "summary": "Led digital product delivery across multiple PODs for CIBC's consumer online and mobile banking experience, used by up to 13 million clients. Owned delivery, roadmap planning, intake, prioritization, and cross-functional execution across multiple Product Owner teams.",
        "bullets": [
            "Reduced annual call center volume by 800,000 through new digital features including Manage My Card, Mobile Chat, and Free Credit Score",
            "Delivered customer-facing digital banking capabilities at enterprise scale through quarterly product increment planning across 80+ concurrent projects",
            "Strengthened the POD operating model by clarifying Product Owner responsibilities, improving decision rights, and creating more consistent ways of working across teams",
        ],
    },
    {
        "title": "Head of Product",
        "company": "Juice Mobile AdTech",
        "dates": "2017 to 2018",
        "summary": "Led product strategy for a Toronto-based mobile AdTech company as the market shifted from managed services toward scalable platform and SaaS-style products. Owned the vision and delivery of three platforms including a DSP, Futures Market, and DMP.",
        "bullets": [
            "Led the SaaS pivot by defining product requirements, user experience, onboarding, support, and commercial expectations for external client-facing software",
            "Built competitive analysis and product strategy for Nectar (Futures Market) and Swarm (DSP), connecting market readiness, platform gaps, customer needs, and revenue opportunity into a practical roadmap",
            "Built margin analysis tools and partnered across Sales, Engineering, and Client Success to balance innovation, usability, profitability, and delivery realities",
        ],
    },
    {
        "title": "Director, Product & Analytics",
        "company": "Rogers Communications",
        "dates": "2013 to 2016",
        "summary": "Led product management for video metadata, search, recommendations, and advanced advertising across Cable TV, Internet, and Home Phone. Managed capital and operating budgets up to $20M. Role sat across product, analytics, first-party data, media partnerships, and executive decision-making during two major platform transformations: the Ignite TV launch and the activation of targeted advertising as a new revenue stream.",
        "bullets": [
            "Launched Canada's first targeted advertising platform inside cable set-top infrastructure, generating $8M+ in first-year revenue",
            "Built VCAR, the subscriber intelligence layer that unlocked first-party viewing data across the Rogers base and turned it into a commercial negotiating asset with content partners",
            "Used first-party subscriber viewership data to renegotiate AMC content rights at a discount, surfacing audience decline trends before the market could price them in",
            "Led analytics and data requirements governance for the Ignite TV launch across 25 teams and 2,000+ requirements",
            "Developed segmentation models clustering usage patterns across 3M customers using 400 variables to improve marketing targeting and reduce call handling times",
        ],
    },
    {
        "title": "Sr. Manager, Strategy & Analytics",
        "company": "Rogers Communications",
        "dates": "2010 to 2012",
        "summary": "Led strategy, planning, and analytics inside the Rogers Anyplace TV incubator, Rogers' first IPTV product. A Sr. Director expanded the role beyond its original scope to include business case development, corporate planning, and product vision after recognizing potential early in the tenure.",
        "bullets": [
            "Led strategic planning for Rogers Anyplace TV, consolidating initiatives across teams, evaluating priorities against goals, and maintaining monthly revenue forecasts with gap and risk analysis",
            "Owned the Adobe Analytics (Omniture SiteCatalyst) environment, rebuilding measurement standards, tagging governance, and digital reporting from the ground up",
            "Built joint digital measurement standards with Rogers Media, establishing shared definitions for video plays and advertising metrics across TV channels, magazines, and the corporate site",
            "Developed the product vision and business case for what later became Shomi, connecting content strategy, market opportunity, customer behaviour, and financial modelling into an executive proposal",
            "Redesigned executive reporting into a monthly visual newsletter format that consistently reached and was read by senior leadership",
        ],
    },
    {
        "title": "Analytics Foundations",
        "company": "Klick Health, Wunderman, Foresters, Enbridge",
        "dates": "2000 to 2010",
        "summary": "A decade building measurement discipline across agency and client-side environments. The through-line across all of it: data is only valuable when it connects to a decision.",
        "bullets": [
            "Klick Health (2009 to 2010): Lead analytics advisor to pharma clients including Pfizer, Amgen, Takeda, and Humana across campaign strategy, CRM optimization, SEM, and media performance",
            "Wunderman (2008 to 2009): Built the agency's digital analytics capability from scratch using Omniture, Google Analytics, and Doubleclick for clients including Ford, Microsoft, Kraft, and the Royal Canadian Mint. Managed a team of four across reporting, digital analytics, and GIS",
            "Foresters and Enbridge: Marketing analytics roles that built the foundational discipline of translating campaign and customer data into direction for business teams that needed decisions, not dashboards",
        ],
    },
]

EDUCATION = {
    "title": "Diploma, Geographic Information Systems",
    "company": "Algonquin College",
    "dates": "1997 to 2000",
    "summary": "The program combined cartography, database design, SQL, and data visualization. The same principle that makes a good map — accurate, readable, and useful — has shaped every BI and executive reporting build since.",
}


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
        return (
            f"Index returned a response, but it could not be parsed. "
            f"Error: {str(e)}. Raw: {response.text[:500]}"
        )


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


def build_api_messages():
    return [
        {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
        for m in st.session_state.messages
    ]


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
            lines.append("## Question")
            lines.append(msg["content"])
            lines.append("")
        else:
            lines.append("## Index")
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


def render_resume_role(role, is_education=False):
    bullets_html = "\n".join(f"<li>{b}</li>" for b in role.get("bullets", []))
    bullets_block = f'<ul class="resume-bullets">{bullets_html}</ul>' if bullets_html else ""
    section_class = "resume-role resume-education" if is_education else "resume-role"
    st.markdown(
        f"""
        <div class="{section_class}">
            <div class="resume-role-header">
                <div class="resume-role-title">{role["title"]}
                    <span class="resume-role-company"> &middot; {role["company"]}</span>
                </div>
                <div class="resume-role-dates">{role["dates"]}</div>
            </div>
            <p class="resume-role-summary">{role["summary"]}</p>
            {bullets_block}
        </div>
        """,
        unsafe_allow_html=True,
    )


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

.stApp {
    background: #FFFFFF;
}

.block-container {
    padding-top: 3.25rem !important;
    padding-bottom: 1.75rem !important;
    max-width: 1220px;
}

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
    padding: 8px 0 24px 0;
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
    font-size: 34px;
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
    margin-bottom: 18px;
    padding-left: 2px;
}

.index-intro {
    font-size: 15px;
    color: #4B5563;
    line-height: 1.65;
    max-width: 860px;
    margin: 0;
}

/* Tabs */
[data-testid="stTabs"] {
    margin-top: 8px;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    background: transparent;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    color: var(--muted);
    font-size: 13.5px;
    font-weight: 600;
    padding: 10px 20px 10px 0;
    margin-right: 24px;
    transition: all 0.15s ease;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--muted-teal);
    background: transparent;
}

[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"],
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"]:focus,
[data-testid="stTabs"] [aria-selected="true"][data-baseweb="tab"]:focus-within {
    color: var(--primary-dark);
    border-bottom: 2px solid var(--muted-teal);
    background: transparent;
    outline: none;
    box-shadow: none;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none;
}

[data-testid="stTabsContent"] {
    padding-top: 20px;
}

/* Chat header */
.chat-card-title {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    color: var(--primary-dark);
    font-size: 13.5px;
    font-weight: 750;
    margin-bottom: 10px;
    margin-top: 0;
}

/* Generic buttons */
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

/* Bordered container */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: 16px !important;
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
    outline: none !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: var(--muted-teal) !important;
    box-shadow: 0 0 0 1px var(--muted-teal) !important;
    outline: none !important;
}

[data-baseweb]:hover,
[data-baseweb]:focus-within {
    border-color: transparent !important;
    box-shadow: none !important;
}

[data-testid="stChatInputContainer"] *:focus,
[data-testid="stChatInputContainer"] *:focus-visible,
[data-testid="stChatInputContainer"] *:focus-within {
    outline: none !important;
    box-shadow: none !important;
    border-color: transparent !important;
}

div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="input"]:focus-within {
    border-color: var(--muted-teal) !important;
    box-shadow: none !important;
}

textarea:focus,
textarea:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}

/* Footer */
.footer-utility-row {
    margin-top: 12px;
    margin-bottom: 2px;
}

div[data-testid="stColumn"]:has(.quiet-action-link) {
    display: flex;
    align-items: center;
    justify-content: center;
}

div[data-testid="stColumn"]:has(.quiet-action-link) .stMarkdown,
div[data-testid="stColumn"]:has(.quiet-action-link) p {
    margin: 0 !important;
    padding: 0 !important;
    display: flex;
    align-items: center;
    justify-content: center;
}

[data-testid="stDownloadButton"],
[data-testid="stLinkButton"] {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 34px;
    margin: 0 !important;
    padding: 0 !important;
}

[data-testid="stDownloadButton"] > button,
[data-testid="stLinkButton"] > a {
    height: 34px !important;
    padding: 0 !important;
    border: none !important;
    background: transparent !important;
    color: var(--muted-teal) !important;
    font-size: 13px !important;
    font-weight: 650 !important;
    box-shadow: none !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
}

[data-testid="stDownloadButton"] > button:hover:not(:disabled),
[data-testid="stLinkButton"] > a:hover {
    background: transparent !important;
    color: var(--primary-dark) !important;
    border: none !important;
}

[data-testid="stDownloadButton"] > button:disabled {
    background: transparent !important;
    border: none !important;
    color: #C4CDD1 !important;
    box-shadow: none !important;
}

.disclaimer {
    text-align: center;
    font-size: 10.5px;
    color: var(--warm-muted);
    font-style: italic;
    margin-top: 6px;
    padding: 0 8px;
    line-height: 1.45;
}

/* Questions tab */
.questions-blurb {
    font-size: 14px;
    color: #4B5563;
    line-height: 1.7;
    max-width: 760px;
    margin-bottom: 32px;
}

.questions-section {
    margin-bottom: 32px;
}

.questions-section-header {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted-teal);
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-soft);
}

.questions-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.questions-list li {
    font-size: 14px;
    color: var(--text);
    padding: 10px 0 10px 20px;
    line-height: 1.5;
    cursor: text;
    user-select: all;
    position: relative;
}

.questions-list li::before {
    content: "•";
    color: var(--muted-teal);
    font-size: 16px;
    position: absolute;
    left: 0;
    top: 9px;
    line-height: 1.5;
}

.questions-list li:hover {
    color: var(--muted-teal);
}

/* Resume tab */
.resume-header {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
}

.resume-name {
    font-size: 28px;
    font-weight: 750;
    color: var(--primary-dark);
    letter-spacing: -0.4px;
    line-height: 1.2;
    margin-bottom: 6px;
}

.resume-tagline {
    font-size: 14px;
    color: var(--warm-muted);
    font-weight: 400;
}

.resume-role {
    padding: 24px 0;
    border-bottom: 1px solid var(--border-soft);
}

.resume-role:last-of-type {
    border-bottom: none;
}

.resume-education {
    margin-top: 8px;
    padding-top: 28px;
    border-top: 1px solid var(--border);
    border-bottom: none;
}

.resume-role-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 10px;
    gap: 16px;
}

.resume-role-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--primary-dark);
    line-height: 1.3;
}

.resume-role-company {
    font-size: 14px;
    font-weight: 400;
    color: var(--muted);
}

.resume-role-dates {
    font-size: 12px;
    font-weight: 600;
    color: var(--muted-teal);
    white-space: nowrap;
    letter-spacing: 0.03em;
}

.resume-role-summary {
    font-size: 13.5px;
    color: #4B5563;
    line-height: 1.65;
    margin-bottom: 14px;
}

.resume-bullets {
    list-style: none;
    padding: 0;
    margin: 0;
}

.resume-bullets li {
    font-size: 13.5px;
    color: var(--text);
    padding: 5px 0 5px 18px;
    line-height: 1.55;
    position: relative;
}

.resume-bullets li::before {
    content: "•";
    color: var(--muted-teal);
    font-size: 15px;
    position: absolute;
    left: 0;
    top: 4px;
    line-height: 1.55;
}

/* Mobile */
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

    .resume-role-header {
        flex-direction: column;
        gap: 4px;
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

    st.markdown(
        """
        <div class="index-header">
            <div class="index-logo-row">
                <span class="index-star">✦</span>
                <span class="index-title">Index</span>
            </div>
            <div class="index-powered">Powered by Snowflake</div>
            <p class="index-intro">
                Index finds what resumes can't — what people say about working with someone,
                how they build high performing teams, the patterns in their work experience.
                All you have to do is ask.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Tabs
    # --------------------------------------------------------

    tab_index, tab_questions, tab_resume = st.tabs(["✦  Ask Index", "  What to Ask", "  Resume Snapshot"])

    # --------------------------------------------------------
    # Tab 1: Ask Index (unchanged)
    # --------------------------------------------------------

    with tab_index:

        st.markdown(
            """
            <div class="chat-card-title">
                <span>Chat with Index</span>
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
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            prompt = st.chat_input("Ask anything about Amy...")

        if "pending_prompt" in st.session_state:
            actual_prompt = st.session_state.pop("pending_prompt")
            display_text = st.session_state.pop("pending_display", actual_prompt)
            ask_index(actual_prompt=actual_prompt, display_text=display_text)

        if prompt:
            ask_index(actual_prompt=prompt, display_text=prompt)

        has_conversation = any(m["role"] == "assistant" for m in st.session_state.messages)

        st.markdown('<div class="footer-utility-row"></div>', unsafe_allow_html=True)

        footer_left, footer_center, footer_right = st.columns([1.2, 1.6, 1.2])

        with footer_center:
            action_col1, action_col2 = st.columns(2)

            with action_col1:
                st.link_button("Connect on LinkedIn", LINKEDIN_URL, use_container_width=True)

            with action_col2:
                st.download_button(
                    label="Download summary",
                    data=build_conversation_markdown(),
                    file_name="Amy_Korosi_Index_Conversation.md",
                    mime="text/markdown",
                    disabled=not has_conversation,
                    use_container_width=True,
                )

        st.markdown(
            """
            <p class="disclaimer">
                Prototype disclosure: Index began May 16, 2026 and is a work in progress.
                Feedback is welcome via LinkedIn.
            </p>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Tab 2: What to Ask
    # --------------------------------------------------------

    with tab_questions:

        st.markdown(
            """
            <p class="questions-blurb">
                These questions are designed to let Index do the synthesis work across
                Amy's Professional Engram. Cut and paste any of them into the Ask Index tab,
                or use them as a starting point and ask in your own words.
            </p>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_spacer, col_right = st.columns([1, 0.1, 1])

        sections = list(QUESTIONS.items())
        left_sections = sections[:2]
        right_sections = sections[2:]

        with col_left:
            for section_title, questions in left_sections:
                items_html = "\n".join(f"<li>{q}</li>" for q in questions)
                st.markdown(
                    f"""
                    <div class="questions-section">
                        <div class="questions-section-header">{section_title}</div>
                        <ul class="questions-list">
                            {items_html}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_right:
            for section_title, questions in right_sections:
                items_html = "\n".join(f"<li>{q}</li>" for q in questions)
                st.markdown(
                    f"""
                    <div class="questions-section">
                        <div class="questions-section-header">{section_title}</div>
                        <ul class="questions-list">
                            {items_html}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --------------------------------------------------------
    # Tab 3: Resume Snapshot
    # --------------------------------------------------------

    with tab_resume:

        st.markdown(
            """
            <div class="resume-header">
                <div class="resume-name">Amy Korosi</div>
                <div class="resume-tagline">Enterprise Data, Technology &amp; AI Leader &nbsp;·&nbsp; Toronto, Ontario</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for role in RESUME:
            render_resume_role(role)

        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

        render_resume_role(EDUCATION, is_education=True)
