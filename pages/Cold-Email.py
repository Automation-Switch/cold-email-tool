import io
import os
import streamlit as st
from crewai import Crew
from cold_EmailAgents import ColdEmailAgents
from cold_EmailTasks import coldEmailTasks
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from streamlit_extras.switch_page_button import switch_page

# Configure Streamlit page
st.set_page_config(page_icon="assets/scaletific_icon.png", layout="wide")

def icon(emoji: str):
    """Display an emoji icon in the Streamlit app."""
    st.write(
        f'<span style="font-size: 38px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

class ColdEmailCrew:
    def __init__(self, industry, sender, briefDes, offer_pdf, offer_link, llm_name):
        self.industry = industry
        self.sender = sender
        self.briefDes = briefDes
        self.offer_pdf = offer_pdf
        self.offer_link = offer_link
        self.llm_name = llm_name
        self.output_placeholder = st.empty()

    def run(self):
        """Execute the tasks and return the contents of the generated files."""
        agents = ColdEmailAgents(llm_name=self.llm_name)  
        tasks = coldEmailTasks()

        # Initialize agents
        business_analyst_agent = agents.business_analyst_agent()
        business_portfolio_analyst_agent = agents.business_portfolio_analyst()
        pain_points_analyst_agent = agents.pain_points_analyst()
        cold_email_generator_agent = agents.cold_email_generator()
        cold_email_reviewer_agent = agents.cold_email_reviewer_agent()  

        # Create tasks with correct argument ordering
        subniche = tasks.subniche(
            agent=business_analyst_agent,
            industry=self.industry,
            sender=self.sender,
            briefDes=self.briefDes,
            offer_pdf=self.offer_pdf,
            offer_link=self.offer_link
        )

        profile = tasks.profile(
            agent=business_portfolio_analyst_agent,
            industry=self.industry,
            sender=self.sender,
            briefDes=self.briefDes,
            offer_pdf=self.offer_pdf,
            offer_link=self.offer_link
        )

        painPoints = tasks.painPoints(
            agent=pain_points_analyst_agent,
            industry=self.industry,
            sender=self.sender,
            briefDes=self.briefDes,
            offer_pdf=self.offer_pdf,
            offer_link=self.offer_link
        )

        coldEmailWriter = tasks.coldEmailWriter(
            agent=cold_email_generator_agent,
            industry=self.industry,
            sender=self.sender,
            briefDes=self.briefDes,
            offer_pdf=self.offer_pdf,
            offer_link=self.offer_link
        )

        coldEmailReviewer = tasks.coldEmailReviewer(
            agent=cold_email_reviewer_agent,
            industry=self.industry,
            sender=self.sender,
            briefDes=self.briefDes,
            offer_pdf=self.offer_pdf,
            offer_link=self.offer_link
        )

        # Initialize and execute the Crew
        crew = Crew(
            agents=[
                business_analyst_agent, 
                business_portfolio_analyst_agent, 
                pain_points_analyst_agent, 
                cold_email_generator_agent, 
                cold_email_reviewer_agent  
            ],
            tasks=[subniche, profile, painPoints, coldEmailWriter, coldEmailReviewer],  
            verbose=True
        )

        crew.kickoff()

        # Read and return the contents of the generated files
        results = {
            #"Companies": self._read_file(tasks.subniche_output_file),
            "Job Titles": self._read_file(tasks.profile_output_file),
            "Pain Points": self._read_file(tasks.painPoints_output_file),
            "Cold Emails": self._read_file(tasks.coldEmailReviewer_output_file),
        }

        return results

    def _read_file(self, file_path):
        """Read the contents of a file if it exists."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            return f"**Error:** The file `{file_path}` was not found."

def create_pdf(content):
    """Generate a PDF from the provided content."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=1*inch, leftMargin=1*inch,
                            topMargin=1*inch, bottomMargin=1*inch)

    styles = getSampleStyleSheet()
    elements = []

    # Add header
    header_text = "Cold Email Report\nhttps://scaletific.com/ - team@scaletific.com"
    header = Paragraph(header_text, styles['Title'])
    elements.append(header)
    elements.append(Spacer(1, 12))

    # Add body content
    for section_title, section_content in content.items():
        section_header = Paragraph(section_title, styles['Heading2'])
        elements.append(section_header)
        elements.append(Spacer(1, 12))
        section_body = Paragraph(section_content, styles['BodyText'])
        elements.append(section_body)
        elements.append(Spacer(1, 24))

    # Add footer
    footer_text = "Page 1"
    footer = Paragraph(footer_text, styles['Normal'])
    elements.append(Spacer(1, 12))
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)

    return buffer

def run_email_generation(industry, sender, briefDes, offer_pdf, offer_link, llm_name):
    """Instantiate and run the ColdEmailCrew, then return the results."""
    email_crew = ColdEmailCrew(industry, sender, briefDes, offer_pdf, offer_link, llm_name)
    results = email_crew.run()
    return results

def set_query_params_via_js(page):
    """Set query parameters via JavaScript for redirection purposes."""
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
    """Main function to run the Streamlit app."""
    # Authentication check
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("You need to be logged in to access this page.")
        login_redirect = st.button("Login")
        if login_redirect:
            switch_page('Home')
        set_query_params_via_js("home")  # Redirect to home if not logged in
        st.stop()

    # Initialize session state variables
    if "show_sidebar" not in st.session_state:
        st.session_state.show_sidebar = True
    if "results" not in st.session_state:
        st.session_state.results = {}
    if "generate" not in st.session_state:
        st.session_state.generate = False

    def toggle_sidebar():
        """Toggle the visibility of the sidebar."""
        st.session_state.show_sidebar = not st.session_state.show_sidebar

    # Sidebar toggle button
    st.button("Main Menu", on_click=toggle_sidebar)

    # Display header and apply custom styles
    icon(":postbox: Cold Email Generator")
    st.subheader("Let AI agents help you land your first client!", anchor=False, divider="rainbow")
    try:
        with open('style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Custom CSS file `style.css` not found. Continuing without custom styles.")

    # Sidebar form for user input
    if st.session_state.show_sidebar:
        with st.sidebar:
            st.header("Fill out the following:")
            with st.form("my_form"):
                # Industry selection
                dropdown_Options = ["Service Providers", "Manufacturing", "Agricultural", "Other"]
                industry = st.selectbox(
                    "Which industry perfectly describes the companies you are sending the cold email to?", 
                    dropdown_Options
                )
                industry_other = st.text_input("If 'Other' please specify", help="Optional")

                # Company and offer details
                sender = st.text_input("What is the name of your Company?", placeholder="Scaletific")
                briefDes = st.text_area("Provide a brief description about the services you offer")
                offer_pdf = st.file_uploader(
                    "Upload a PDF file of the services you offer", 
                    type="pdf", 
                    key="pdf_uploader", 
                    help="Optional: Upload a PDF file for your services"
                )
                offer_link = st.text_input("Provide a link to your website", help="Optional: Provide a link to your services")

                # Language model selection
                llm_options = ["cohere", "openai", "groq"]
                llm_name = st.selectbox("Select an LLM", llm_options)

                # Submit button
                submitted = st.form_submit_button("Generate Cold Email")

                if submitted:
                    # Save inputs to session state
                    st.session_state.industry = industry if industry != "Other" else industry_other
                    st.session_state.sender = sender
                    st.session_state.briefDes = briefDes
                    st.session_state.offer_pdf = offer_pdf
                    st.session_state.offer_link = offer_link
                    st.session_state.llm_name = llm_name
                    st.session_state.generate = True

    # Execute email generation when triggered
    if st.session_state.generate:
        with st.spinner("Agents at work..."):
            st.session_state.results = run_email_generation(
                st.session_state.industry, 
                st.session_state.sender, 
                st.session_state.briefDes, 
                st.session_state.offer_pdf, 
                st.session_state.offer_link, 
                st.session_state.llm_name
            )
        st.session_state.generate = False

    # Display results and provide PDF download
    if st.session_state.results:
        for title, content in st.session_state.results.items():
            st.subheader(title)
            st.markdown(content)

        # Prepare content for PDF
        pdf_content = st.session_state.results
        pdf_data = create_pdf(pdf_content)

        # Download button for PDF
        st.download_button(
            label="Download Results as PDF",
            data=pdf_data,
            file_name="Cold-Email-Results.pdf",
            mime="application/pdf"
        )

    # Footer
    st.markdown("*Copyright ©2024 [Scaletific](https://www.scaletific.com). All Rights Reserved.*")

if __name__ == "__main__":
    main()
