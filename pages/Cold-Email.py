import io
import os
import streamlit as st
from crewai import Crew
from cold_EmailAgents import ColdEmailAgents
from cold_EmailTasks import coldEmailTasks
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF
from streamlit_extras.switch_page_button import switch_page
from supabase_client import get_supabase

FREE_RUN_LIMIT = 3

st.set_page_config(page_icon="assets/scaletific_icon.png", layout="wide", page_title="PrecisionReach")

# ── Global styles ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { visibility: hidden; display: none; }

/* ── Main background ── */
.stApp { background-color: #0a0a0a; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0f0f0f;
    border-right: 1px solid #1e1e1e;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #C8FF00;
    font-weight: 600;
    letter-spacing: -0.02em;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent;
    color: #C8FF00;
    border: 1px solid #C8FF00;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    padding: 6px 16px;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #C8FF00;
    color: #0a0a0a;
}

/* ── Form submit button ── */
.stFormSubmitButton > button {
    background: #C8FF00 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.15s ease !important;
}
.stFormSubmitButton > button:hover {
    background: #d4ff33 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent;
    color: #C8FF00;
    border: 1px solid #C8FF00;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    transition: all 0.15s ease;
}
.stDownloadButton > button:hover {
    background: #C8FF00;
    color: #0a0a0a;
}

/* ── Inputs ── */
.stTextInput input,
.stTextArea textarea {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    color: #f0f0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.15s ease;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #C8FF00 !important;
    box-shadow: 0 0 0 1px #C8FF00 !important;
}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 6px !important;
    color: #f0f0f0 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #111;
    border: 1px dashed #2a2a2a;
    border-radius: 8px;
    padding: 8px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #C8FF00;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    margin-bottom: 12px;
}
[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #f0f0f0;
    padding: 12px 16px;
}
[data-testid="stExpander"] summary:hover {
    color: #C8FF00;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #C8FF00, #a8e000) !important;
    border-radius: 4px;
}
.stProgress > div > div {
    background: #1a1a1a !important;
    border-radius: 4px;
}

/* ── Metric ── */
[data-testid="metric-container"] {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 12px 16px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #C8FF00;
    font-family: 'DM Mono', monospace;
    font-size: 28px;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #666;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Alerts ── */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 6px;
    border-left: 3px solid;
}
.stSuccess { border-color: #C8FF00; }
.stInfo    { border-color: #4488ff; }
.stWarning { border-color: #ffaa00; }
.stError   { border-color: #ff4444; }

/* ── Divider ── */
hr { border-color: #1e1e1e !important; }

/* ── Code blocks (used for copy) ── */
.stCode {
    background: #111 !important;
    border: 1px solid #1e1e1e;
    border-radius: 6px;
}

/* ── Section labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Supabase helpers
# ─────────────────────────────────────────

def get_run_count(user_id: str):
    try:
        sb = get_supabase()
        result = sb.table("user_profiles").select("run_count, is_paid").eq("id", user_id).single().execute()
        if result.data:
            return result.data.get("run_count", 0), result.data.get("is_paid", False)
    except Exception:
        pass
    return 0, False


def increment_run_count(user_id: str):
    try:
        sb = get_supabase()
        current, _ = get_run_count(user_id)
        sb.table("user_profiles").upsert({"id": user_id, "run_count": current + 1}).execute()
    except Exception as e:
        st.warning(f"Could not update run count: {e}")


def save_run_to_supabase(user_id: str, industry: str, sender: str, briefDes: str,
                          offer_link: str, llm_name: str, results: dict):
    try:
        sb = get_supabase()
        sb.table("runs").insert({
            "user_id":     user_id,
            "industry":    industry,
            "sender":      sender,
            "brief_des":   briefDes,
            "offer_link":  offer_link,
            "llm_name":    llm_name,
            "job_titles":  results.get("Job Titles", ""),
            "pain_points": results.get("Pain Points", ""),
            "cold_emails": results.get("Cold Emails", ""),
        }).execute()
    except Exception as e:
        st.warning(f"Could not save run: {e}")


# ─────────────────────────────────────────
# PDF text extraction
# ─────────────────────────────────────────

def extract_pdf_text(uploaded_file) -> str:
    """Extract plain text from an uploaded PDF file object."""
    if uploaded_file is None:
        return ""
    try:
        import pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
    except Exception:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


# ─────────────────────────────────────────
# Crew runner
# ─────────────────────────────────────────

STAGES = [
    {"step": 1, "icon": "🔍", "label": "Researching your industry and target companies..."},
    {"step": 2, "icon": "👥", "label": "Profiling job titles and decision-makers..."},
    {"step": 3, "icon": "💡", "label": "Building ideal customer profiles..."},
    {"step": 4, "icon": "✉️",  "label": "Drafting your cold emails..."},
]


def render_stages(completed: int, status_box):
    lines = []
    for s in STAGES:
        if s["step"] < completed:
            lines.append(f"✅ ~~{s['label']}~~")
        elif s["step"] == completed:
            lines.append(f"{s['icon']} **{s['label']}**")
        else:
            lines.append(f"⬜ {s['label']}")
    status_box.markdown("\n\n".join(lines))


class ColdEmailCrew:
    def __init__(self, industry, sender, briefDes, offer_pdf_text, offer_link,
                 llm_name, byok_key=None, status_box=None, progress_bar=None):
        self.industry      = industry
        self.sender        = sender
        self.briefDes      = briefDes
        self.offer_pdf     = offer_pdf_text   # plain text, not file object
        self.offer_link    = offer_link
        self.llm_name      = llm_name
        self.byok_key      = byok_key
        self.status_box    = status_box
        self.progress_bar  = progress_bar
        self._stage        = [1]

    def _on_task_complete(self, output):
        completed = self._stage[0]
        if self.progress_bar:
            self.progress_bar.progress(completed / len(STAGES))
        if self.status_box:
            render_stages(completed + 1, self.status_box)
        self._stage[0] += 1

    def run(self):
        if self.status_box:
            render_stages(1, self.status_box)
        if self.progress_bar:
            self.progress_bar.progress(0)

        agents = ColdEmailAgents(llm_name=self.llm_name, byok_key=self.byok_key)
        tasks  = coldEmailTasks()

        business_analyst_agent           = agents.business_analyst_agent()
        business_portfolio_analyst_agent = agents.business_portfolio_analyst()
        idealCustomer_profiler           = agents.idealCustomer_profiler()
        cold_email_generator_agent       = agents.cold_email_generator()

        kwargs = dict(
            industry=self.industry, sender=self.sender,
            briefDes=self.briefDes, offer_pdf=self.offer_pdf,
            offer_link=self.offer_link,
        )

        subniche             = tasks.subniche(agent=business_analyst_agent, **kwargs)
        profile              = tasks.profile(agent=business_portfolio_analyst_agent, **kwargs)
        idealCustomerProfile = tasks.idealCustomerProfile(agent=idealCustomer_profiler, **kwargs)
        coldEmailWriter      = tasks.coldEmailWriter(agent=cold_email_generator_agent, **kwargs)

        crew = Crew(
            agents=[business_analyst_agent, business_portfolio_analyst_agent,
                    idealCustomer_profiler, cold_email_generator_agent],
            tasks=[subniche, profile, idealCustomerProfile, coldEmailWriter],
            task_callback=self._on_task_complete,
            verbose=True,
        )
        crew.kickoff()

        if self.progress_bar:
            self.progress_bar.progress(1.0)
        if self.status_box:
            self.status_box.markdown("✅ **All agents complete. Your campaign is ready.**")

        return {
            "Job Titles":  self._read_file(tasks.profile_output_file),
            "Pain Points": self._read_file(tasks.painPoints_output_file),
            "Cold Emails": self._read_file(tasks.coldEmailReviewer_output_file),
        }

    def _read_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        return f"**Error:** File `{file_path}` not found."


# ─────────────────────────────────────────
# PDF export
# ─────────────────────────────────────────

def create_pdf(results: dict) -> io.BytesIO:
    pdf    = Document()
    page   = Page()
    pdf.append_page(page)
    layout = SingleColumnLayout(page)
    for title, content in results.items():
        layout.add(Paragraph(title, font_size=14))
        layout.add(Paragraph(content, font="Helvetica", font_size=8))
    buf = io.BytesIO()
    PDF.write(buf, pdf)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────
# Main app
# ─────────────────────────────────────────

def main():
    # ── Auth guard ──
    if not st.session_state.get("logged_in") or not st.session_state.get("user"):
        st.warning("Please log in to access PrecisionReach.")
        if st.button("Go to Login"):
            switch_page("Home")
        st.stop()

    user    = st.session_state["user"]
    user_id = user.id

    # ── Freemium gate ──
    run_count, is_paid = get_run_count(user_id)
    runs_remaining = max(0, FREE_RUN_LIMIT - run_count)

    # ── Session state init ──
    for key, default in [("show_sidebar", True), ("results", {}),
                          ("generate", False), ("pdf_data", None)]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── Header ──
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("""
        <div style="padding: 8px 0 4px 0;">
            <span style="font-size:11px; font-family:'DM Mono',monospace; letter-spacing:0.12em;
                         text-transform:uppercase; color:#555;">Automation Switch</span>
            <h1 style="margin:4px 0 0 0; font-size:28px; font-weight:700;
                       letter-spacing:-0.03em; color:#f0f0f0; line-height:1.1;">
                PrecisionReach
            </h1>
            <p style="margin:6px 0 0 0; color:#555; font-size:14px;">
                AI agents that research your market and write your cold emails.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not is_paid:
            st.metric("Free runs left", runs_remaining)

    st.divider()

    # ── Sidebar toggle ──
    if st.button("☰  Campaign Details"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    # ── Sidebar form ──
    if st.session_state.show_sidebar:
        with st.sidebar:
            st.markdown("""
            <div style="padding: 16px 0 8px 0;">
                <span style="font-size:10px; font-family:'DM Mono',monospace; letter-spacing:0.12em;
                             text-transform:uppercase; color:#444;">Campaign Setup</span>
            </div>
            """, unsafe_allow_html=True)

            with st.form("campaign_form"):
                industry_options = ["Real Estate", "Service Providers", "Manufacturing",
                                    "Technology", "Healthcare", "Financial Services",
                                    "Retail", "Agricultural", "Other"]
                industry       = st.selectbox("Target Industry", industry_options)
                industry_other = st.text_input("If 'Other', specify industry")
                sender         = st.text_input("Your Company Name", placeholder="Automation Switch")
                briefDes       = st.text_area("Describe your services",
                                              placeholder="We help sales teams automate outreach using AI...",
                                              height=120)
                offer_pdf      = st.file_uploader("Upload services PDF (optional)", type="pdf")
                if offer_pdf:
                    st.caption(f"✓ {offer_pdf.name} uploaded")
                offer_link     = st.text_input("Your website URL (optional)")

                st.markdown("<div style='margin:8px 0 4px 0; font-size:11px; color:#555; font-family:DM Mono,monospace; letter-spacing:0.08em; text-transform:uppercase;'>AI Model</div>", unsafe_allow_html=True)
                llm_options = ["claude (managed)", "openai (managed)", "groq (free)", "bring your own key"]
                llm_choice  = st.selectbox("AI Model", llm_options, label_visibility="collapsed")

                byok_key = None
                if llm_choice == "bring your own key":
                    st.markdown("**BYOK — Bring Your Own Key**")
                    byok_provider = st.selectbox("Your provider", ["claude", "openai", "groq"])
                    byok_key      = st.text_input("Paste your API key", type="password",
                                                  help="Used only for this session. Never stored.")
                    llm_name = byok_provider
                else:
                    llm_name = llm_choice.split(" ")[0]

                submitted = st.form_submit_button("Generate Cold Emails →", use_container_width=True)

                if submitted:
                    if llm_choice == "bring your own key" and not byok_key:
                        st.error("Please paste your API key to use BYOK.")
                    elif not is_paid and run_count >= FREE_RUN_LIMIT and llm_choice != "bring your own key":
                        st.error(f"You've used all {FREE_RUN_LIMIT} free runs. Use BYOK or upgrade.")
                    else:
                        pdf_text = extract_pdf_text(offer_pdf) if offer_pdf else ""
                        st.session_state.industry   = industry if industry != "Other" else industry_other
                        st.session_state.sender     = sender
                        st.session_state.briefDes   = briefDes
                        st.session_state.offer_pdf  = pdf_text
                        st.session_state.offer_link = offer_link
                        st.session_state.llm_name   = llm_name
                        st.session_state.byok_key   = byok_key
                        st.session_state.generate   = True
                        st.session_state.results    = {}
                        st.session_state.pdf_data   = None

    # ── Generation ──
    if st.session_state.generate:
        if not st.session_state.results:
            is_byok = bool(st.session_state.get("byok_key"))
            if not is_paid and not is_byok and run_count >= FREE_RUN_LIMIT:
                st.warning(f"You've used all {FREE_RUN_LIMIT} free runs.")
                st.info("Want unlimited access? Email **hello@automationswitch.com** to upgrade.")
                st.session_state.generate = False
                st.stop()

            st.markdown("""
            <div style="padding:16px; background:#0f0f0f; border:1px solid #1e1e1e;
                        border-radius:8px; margin-bottom:16px;">
                <span style="font-size:11px; font-family:'DM Mono',monospace; letter-spacing:0.1em;
                             text-transform:uppercase; color:#555;">Status</span>
                <p style="margin:6px 0 0 0; color:#f0f0f0; font-size:15px; font-weight:500;">
                    🤖 Agents at work — this takes 3–5 minutes
                </p>
            </div>
            """, unsafe_allow_html=True)

            progress_bar = st.progress(0)
            status_box   = st.empty()

            crew = ColdEmailCrew(
                st.session_state.industry,
                st.session_state.sender,
                st.session_state.briefDes,
                st.session_state.offer_pdf,
                st.session_state.offer_link,
                st.session_state.llm_name,
                byok_key=st.session_state.get("byok_key"),
                status_box=status_box,
                progress_bar=progress_bar,
            )
            results = crew.run()
            st.session_state.results = results

            save_run_to_supabase(
                user_id=user_id,
                industry=st.session_state.industry,
                sender=st.session_state.sender,
                briefDes=st.session_state.briefDes,
                offer_link=st.session_state.offer_link or "",
                llm_name=st.session_state.llm_name,
                results=results,
            )
            increment_run_count(user_id)
            st.success("✅ Campaign ready.")

        # ── Results ──
        section_icons = {
            "Job Titles":  "👥",
            "Pain Points": "💡",
            "Cold Emails": "✉️",
        }
        for section, content in st.session_state.results.items():
            icon = section_icons.get(section, "📄")
            with st.expander(f"{icon}  {section}", expanded=(section == "Cold Emails")):
                st.markdown(f"<p class='section-label'>Copy the raw text below</p>", unsafe_allow_html=True)
                st.code(content, language="markdown")

        st.divider()

        # ── PDF export ──
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("📥 Generate PDF"):
                st.session_state.pdf_data = create_pdf(st.session_state.results)
        if st.session_state.pdf_data:
            with col_b:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=st.session_state.pdf_data,
                    file_name=f"precision_reach_{st.session_state.industry.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )

        # ── Freemium nudge ──
        if not is_paid:
            new_count = run_count + 1
            if new_count >= FREE_RUN_LIMIT:
                st.warning("⚠️ This was your last free run. Email **hello@automationswitch.com** to unlock unlimited access.")
            else:
                st.info(f"💡 {FREE_RUN_LIMIT - new_count} free run(s) remaining.")


if __name__ == "__main__":
    main()
