import io
import os
import streamlit as st
import streamlit.components.v1 as components
from crewai import Crew
from cold_EmailAgents import ColdEmailAgents
from cold_EmailTasks import coldEmailTasks
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF
from streamlit_extras.switch_page_button import switch_page
from supabase_client import get_supabase

FREE_RUN_LIMIT = 3

st.set_page_config(page_icon="assets/scaletific_icon.png", layout="wide", page_title="PrecisionReach")

# ── Hide Streamlit branding ──
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    [data-testid="stDecoration"] {display: none;}
    </style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Supabase helpers
# ─────────────────────────────────────────

def get_run_count(user_id: str) -> int:
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
            "user_id":    user_id,
            "industry":   industry,
            "sender":     sender,
            "brief_des":  briefDes,
            "offer_link": offer_link,
            "llm_name":   llm_name,
            "job_titles": results.get("Job Titles", ""),
            "pain_points": results.get("Pain Points", ""),
            "cold_emails": results.get("Cold Emails", ""),
        }).execute()
    except Exception as e:
        st.warning(f"Could not save run: {e}")


# ─────────────────────────────────────────
# Crew runner
# ─────────────────────────────────────────

# Stage definitions — order matches task execution order
STAGES = [
    {"step": 1, "icon": "🔍", "label": "Researching your industry and target companies..."},
    {"step": 2, "icon": "👥", "label": "Profiling job titles and decision-makers..."},
    {"step": 3, "icon": "💡", "label": "Building ideal customer profiles..."},
    {"step": 4, "icon": "✉️",  "label": "Drafting your cold emails..."},
]


def render_stages(completed: int, status_box):
    """Render the stage progress tracker inside a Streamlit placeholder."""
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
    def __init__(self, industry, sender, briefDes, offer_pdf, offer_link,
                 llm_name, byok_key=None, status_box=None, progress_bar=None):
        self.industry     = industry
        self.sender       = sender
        self.briefDes     = briefDes
        self.offer_pdf    = offer_pdf
        self.offer_link   = offer_link
        self.llm_name     = llm_name
        self.byok_key     = byok_key
        self.status_box   = status_box
        self.progress_bar = progress_bar
        self._stage       = [1]  # mutable so callback can update it

    def _on_task_complete(self, output):
        """Called by CrewAI after each task finishes."""
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

        subniche = tasks.subniche(
            agent=business_analyst_agent,
            industry=self.industry, sender=self.sender,
            briefDes=self.briefDes, offer_pdf=self.offer_pdf, offer_link=self.offer_link
        )
        profile = tasks.profile(
            agent=business_portfolio_analyst_agent,
            industry=self.industry, sender=self.sender,
            briefDes=self.briefDes, offer_pdf=self.offer_pdf, offer_link=self.offer_link
        )
        idealCustomerProfile = tasks.idealCustomerProfile(
            agent=idealCustomer_profiler,
            industry=self.industry, sender=self.sender,
            briefDes=self.briefDes, offer_pdf=self.offer_pdf, offer_link=self.offer_link
        )
        coldEmailWriter = tasks.coldEmailWriter(
            agent=cold_email_generator_agent,
            industry=self.industry, sender=self.sender,
            briefDes=self.briefDes, offer_pdf=self.offer_pdf, offer_link=self.offer_link
        )

        crew = Crew(
            agents=[business_analyst_agent, business_portfolio_analyst_agent,
                    idealCustomer_profiler, cold_email_generator_agent],
            tasks=[subniche, profile, idealCustomerProfile, coldEmailWriter],
            task_callback=self._on_task_complete,
            verbose=True
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
            with open(file_path, 'r') as f:
                return f.read()
        return f"**Error:** File `{file_path}` not found."


# ─────────────────────────────────────────
# PDF generation
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
# Copy to clipboard component
# ─────────────────────────────────────────

def copy_button(text: str, key: str):
    safe = text.replace("`", "\\`").replace("$", "\\$")
    components.html(f"""
        <button onclick="navigator.clipboard.writeText(`{safe}`).then(() => {{
            this.innerText = '✓ Copied!';
            setTimeout(() => this.innerText = 'Copy to Clipboard', 2000);
        }})" style="
            background:#1a1a1a; color:#C8FF00; border:1px solid #333;
            padding:6px 14px; border-radius:6px; cursor:pointer;
            font-size:13px; font-family:monospace; margin-bottom:8px;
        ">Copy to Clipboard</button>
    """, height=48)


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
        st.markdown("## ✉️ PrecisionReach")
        st.markdown("##### Let AI agents research and write your cold emails.")
    with col2:
        if not is_paid:
            st.metric("Free runs left", runs_remaining)

    st.divider()

    # ── Sidebar toggle ──
    if st.button("☰ Menu"):
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    # ── Sidebar form ──
    if st.session_state.show_sidebar:
        with st.sidebar:
            st.header("Campaign Details")
            with st.form("campaign_form"):
                industry_options = ["Real Estate", "Service Providers", "Manufacturing",
                                    "Technology", "Healthcare", "Financial Services",
                                    "Retail", "Agricultural", "Other"]
                industry      = st.selectbox("Target Industry", industry_options)
                industry_other = st.text_input("If 'Other', specify industry")
                sender        = st.text_input("Your Company Name", placeholder="Automation Switch")
                briefDes      = st.text_area("Describe your services", placeholder="We help sales teams automate outreach using AI...")
                offer_pdf     = st.file_uploader("Upload services PDF (optional)", type="pdf")
                offer_link    = st.text_input("Your website URL (optional)")
                llm_options   = ["claude (managed)", "openai (managed)", "groq (free)", "bring your own key"]
                llm_choice    = st.selectbox("AI Model", llm_options)

                byok_key = None
                if llm_choice == "bring your own key":
                    st.markdown("**BYOK — Bring Your Own Key**")
                    byok_provider = st.selectbox("Your provider", ["claude", "openai", "groq"])
                    byok_key      = st.text_input("Paste your API key", type="password",
                                                  help="Your key is used only for this session and never stored.")
                    llm_name = byok_provider
                else:
                    llm_name = llm_choice.split(" ")[0]  # strip "(managed)" / "(free)"

                submitted = st.form_submit_button("Generate Cold Emails", use_container_width=True)

                if submitted:
                    if llm_choice == "bring your own key" and not byok_key:
                        st.error("Please paste your API key to use BYOK.")
                    elif not is_paid and run_count >= FREE_RUN_LIMIT and llm_choice != "bring your own key":
                        st.error(f"You've used all {FREE_RUN_LIMIT} free runs. Use BYOK or upgrade.")
                    else:
                        st.session_state.industry   = industry if industry != "Other" else industry_other
                        st.session_state.sender     = sender
                        st.session_state.briefDes   = briefDes
                        st.session_state.offer_pdf  = offer_pdf
                        st.session_state.offer_link = offer_link
                        st.session_state.llm_name   = llm_name
                        st.session_state.byok_key   = byok_key
                        st.session_state.generate   = True
                        st.session_state.results    = {}
                        st.session_state.pdf_data   = None

    # ── Generation ──
    if st.session_state.generate:
        if not st.session_state.results:

            # Final freemium check — BYOK users bypass the run limit
            is_byok = bool(st.session_state.get("byok_key"))
            if not is_paid and not is_byok and run_count >= FREE_RUN_LIMIT:
                st.warning(f"You've used all {FREE_RUN_LIMIT} free runs.")
                st.info("Want unlimited access? Email us at **hello@automationswitch.com** to upgrade.")
                st.session_state.generate = False
                st.stop()

            st.markdown("#### 🤖 Agents at work — this takes 3–5 minutes")
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

            # Save to Supabase + increment counter
            save_run_to_supabase(
                user_id=user_id,
                industry=st.session_state.industry,
                sender=st.session_state.sender,
                briefDes=st.session_state.briefDes,
                offer_link=st.session_state.offer_link or "",
                llm_name=st.session_state.llm_name,
                results=results
            )
            increment_run_count(user_id)
            st.success("✅ Done! Your cold email campaign is ready.")

        # ── Display results ──
        for section, content in st.session_state.results.items():
            with st.expander(f"📄 {section}", expanded=True):
                copy_button(content, key=section)
                st.markdown(content)

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
                    mime="application/pdf"
                )

        # ── Freemium nudge ──
        if not is_paid:
            new_count = run_count + 1
            if new_count >= FREE_RUN_LIMIT:
                st.warning(f"⚠️ This was your last free run. Email **hello@automationswitch.com** to unlock unlimited access.")
            else:
                st.info(f"💡 You have {FREE_RUN_LIMIT - new_count} free run(s) remaining.")


if __name__ == "__main__":
    main()
