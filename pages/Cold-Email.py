import io
import streamlit as st
from crewai import Crew
from cold_EmailAgents import ColdEmailAgents
from cold_EmailTasks import coldEmailTasks
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_icon="assets/scaletific_icon.png", layout="wide")

def icon(emoji: str):
    st.write(
        f'<span style="font-size: 38px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

class ColdEmailCrew:
    def __init__(self, industry, sender, briefDes, offer_pdf, offer_link):
        self.industry = industry
        self.sender = sender
        self.briefDes = briefDes
        self.offer_pdf = offer_pdf
        self.offer_link = offer_link
        self.output_placeholder = st.empty()

    def run(self):
        agents = ColdEmailAgents()  
        tasks = coldEmailTasks()

        business_analyst_agent = agents.business_analyst_agent()
        business_portfolio_analyst_agent = agents.business_portfolio_analyst()
        pain_points_analyst_agent = agents.pain_points_analyst()
        cold_email_generator_agent = agents.cold_email_generator()
        cold_email_reviewer_agent = agents.cold_email_reviewer_agent()  

        subniche = tasks.subniche(
            business_analyst_agent, self.briefDes, self.industry, self.sender, self.offer_link, self.offer_pdf
        )

        profile = tasks.profile(
            business_portfolio_analyst_agent, self.briefDes, self.industry, self.offer_pdf, self.offer_link, self.sender
        )

        painPoints = tasks.painPoints(
            pain_points_analyst_agent, self.industry, self.briefDes, self.offer_pdf, self.offer_link, self.sender
        )

        coldEmailWriter = tasks.coldEmailWriter(
            cold_email_generator_agent, self.briefDes, self.industry, self.offer_link, self.offer_pdf, self.sender
        )

        coldEmailReviewer = tasks.coldEmailReviewer(
            cold_email_reviewer_agent, self.briefDes, self.industry, self.offer_link, self.offer_pdf, self.sender
        )

        crew = Crew(
            agents=[
                business_analyst_agent, business_portfolio_analyst_agent, pain_points_analyst_agent, 
                cold_email_generator_agent, cold_email_reviewer_agent  
            ],
            tasks=[subniche, profile, painPoints, coldEmailWriter, coldEmailReviewer],  
            verbose=True
        )

        result = crew.kickoff()
        self.output_placeholder.markdown(result)
        return result

def create_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=1*inch, leftMargin=1*inch,
                            topMargin=1*inch, bottomMargin=1*inch)

    styles = getSampleStyleSheet()
    elements = []

    header_text = "Cold Email\nhttps://scaletific.com/ - team@scaletific.com"
    header = Paragraph(header_text, styles['Title'])
    elements.append(header)
    elements.append(Spacer(1, 12))

    body = Paragraph(content, styles['BodyText'])
    elements.append(body)
    elements.append(Spacer(1, 12))

    footer_text = "Page 1"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(Spacer(1, 12))
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)

    return buffer

def run_email_generation(industry, sender, briefDes, offer_pdf, offer_link):
    email_crew = ColdEmailCrew(industry, sender, briefDes, offer_pdf, offer_link)
    result = email_crew.run()
    return result

def set_query_params_via_js(page):
    js_code = f"""
    <script>
    function setQueryParams() {{
        const url = new URL(window.location);
        url.searchParams.set('page', '{page}');
        window.history.pushState('', '', url);
    }}
    setQueryParams();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def main():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You need to be logged in to access this page.")
        set_query_params_via_js("home")  # Set page query parameter to redirect
        st.stop()

    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = True
    if "result" not in st.session_state:
        st.session_state.result = ""
    if "generate" not in st.session_state:
        st.session_state.generate = False

    def toggle_sidebar():
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    st.button("Main Menu", on_click=toggle_sidebar)

    icon(":postbox: Cold Email Generator")
    st.subheader("Let AI agents help you land your first client!", divider="rainbow", anchor=False)
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    if st.session_state.show_sidebar:
        with st.sidebar:
            st.header("Fill out the following:")
            with st.form("my_form"):
                dropdown_Options = ["Service Providers", "Manufacturing", "Agricultural", "Other"]
                industry = st.selectbox("Which industry perfectly describes the companies you are sending the cold email to?", dropdown_Options)
                industry_other = st.text_input("If 'Other' please specify", help="Optional")
                sender = st.text_input("What is the name of your Company?", placeholder="Scaletific")
                briefDes = st.text_area("Provide a brief description about the services you offer")
                offer_pdf = st.file_uploader("Upload a PDF file of the services you offer", type="pdf", key="pdf_uploader", help="Optional: Upload a PDF file for your services")
                offer_link = st.text_input("Provide a link to website", help="Optional: Provide a link to your services")
            

                submitted = st.form_submit_button("Generate Cold Email")

                if submitted:
                    st.session_state.industry = industry if industry != "Other" else industry_other
                    st.session_state.sender = sender
                    st.session_state.briefDes = briefDes
                    st.session_state.offer_pdf = offer_pdf
                    st.session_state.offer_link = offer_link
                    st.session_state.generate = True

    if st.session_state.generate:
        with st.spinner("Agents at work..."):
            st.session_state.result = run_email_generation(
                st.session_state.industry, st.session_state.sender, st.session_state.briefDes, st.session_state.offer_pdf, st.session_state.offer_link
            )
        st.session_state.generate = False

    if st.session_state.result:
        st.subheader("Here is your Cold Email", anchor=False, divider="rainbow")
        st.markdown(st.session_state.result)

        pdf_content = str(st.session_state.result)  # Ensure result is a string
        pdf_data = create_pdf(pdf_content)
        st.download_button(
            label="Download Cold Email as PDF",
            data=pdf_data,
            file_name="Cold-Email.pdf",
            mime="application/pdf"
        )

    st.markdown("*Copyright ©2024 [Scaletific](https://www.scaletific.com). All Rights Reserved.*")

if __name__ == "__main__":
    main()
