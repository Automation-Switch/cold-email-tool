from crewai import Agent
import streamlit as st
from langchain_groq import ChatGroq
from tools.search_tools import SearchTools

def streamlit_callback(step_output):
    st.markdown("---")
    
    for step in step_output:
        if isinstance(step, tuple) and len(step) == 2:
            _, observation = step
            
            # Define the text to filter out
            text_to_filter = """You ONLY have access to the following tools, and should NEVER make up tools that are not listed here:
                             Search the internet: Search the internet(query) - Useful to search the internet
                             about a given topic and return relevant results
                             Use the following format:
                             Thought: you should always think about what to do
                             Action: the action to take, only one name of [Search the internet], just the name, exactly as it's written.
                             Action Input: the input to the action, just a simple python dictionary using " to wrap keys and values.Observation: the result of the action
                             Once all necessary information is gathered:
                             Thought: I now know the final answer"""
            
            if "Final Answer:" in observation and text_to_filter not in observation:
                st.markdown("## Observation")
                if isinstance(observation, str):
                    observation_lines = observation.split('\n')
                    for line in observation_lines:
                        if line.startswith('Final Answer:'):
                            st.markdown("**Final Answer:**")
                        else:
                            st.markdown(line)
                else:
                    st.markdown(str(observation))
        else:
            st.markdown(step)

class ColdEmailAgents:

    def __init__(self, model_name):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=st.secrets['GROQ_API_KEY'],
            model_name=model_name,
        )

    def business_analyst_agent(self):
        return Agent(
            role='Business Analyst',
            goal="Identify the companies and subniches within {industry}.",
            backstory="""You are a business analyst, and your primary function is to identify companies/businesses and their specific subniches
                    within {industry} and the broader industry at large. Additionally, you need to assess the services that {sender} offers which will be beneficial to companies within {industry}.
                    With this information, you aid businesses in targeting precise market segments. You collect information from {offer_pdf}, {briefDes} or {offer_link}, {industry}, {sender}.
                    Armed with these details, conduct thorough research on the current companies and subniches within {industry} and the services that {sender} offers that will be beneficial to the companies identified.""",
            tools=[
                SearchTools.search_internet,
            ],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            ##step_callback=streamlit_callback,
        )

    def business_portfolio_analyst(self):
        return Agent(
            role='Business Portfolio Analyst',
            goal="""Identify and list the companies and Job Titles within {industry} that are responsible for or will benefit from {offer_link} or {offer_pdf}, 
            and the supervisor in charge of the Job Titles.""",
            backstory="""You are a Business Portfolio Analyst that identifies relevant companies and job titles within {industry}
                    that would benefit from {offer_link}, {briefDes}, or {offer_pdf}. You analyze information from the Business Analyst and based on its output, make this decision.
                    Your mission is to enhance cold campaigns by targeting Job Titles and the supervisors of these Job titles who are the final decision-makers.""",
    
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            ##step_callback=streamlit_callback,
        )

    def pain_points_analyst(self):
        return Agent(
            role='Business Pain Points Analyst',
            goal="""Identify pain points of Job Titles within each company provided by the Business Portfolio Analyst, 
            ranking them by their contribution to loss of revenue.""",
            backstory="""You are a Business Pain Points Analyst who identifies the key pain points of job titles provided by the Business Portfolio Analyst,
                    ranking the key pain points in order of the intensity of their impact on revenue.
                    You also filter the pain points and identify the solutions that were used to address them in the past. You base your ranking on reviews and sentiments from the targeted Job Titles of various companies within {industry}.""",
        
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            ##step_callback=streamlit_callback,
        )
    
    def cold_email_generator(self):
        return Agent(
            role='Cold Email Generator',
            goal="""Generate cold emails in less than 100 words for the various Job Titles within the companies listed provided by the Business Portfolio Analyst.""",
            backstory="""You are a cold email writer who takes into account the information and details provided by the Business Analyst, the Business Portfolio Analyst,
                    and the Business Pain Points Analyst. Write a non-salesy cold email that addresses the Job Titles and their companies that struggled with the pain points identified by the Business Pain Points Analyst. 
                    Mention that {sender} has specifically helped a similar company that struggled with the same problem in the past.
                    Include in each email a bullet point of the pain points trying to be addressed, the industry, and modern solutions to address the pain point.
                    Use this template:
                    Pain point:
                    Company: 
                    Industry:
                    Modern Solution:
                    Cold Email:""",
            
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            ##step_callback=streamlit_callback,
        )

    def cold_email_reviewer_agent(self):
        return Agent(
            role='Cold Email Reviewer',
            goal="""Review the generated cold emails to ensure they follow the format: 'Title: Painpoint: Job title: email:' for a total of five emails.""",
            backstory="""You are responsible for reviewing cold emails to ensure they adhere to a specific format. This format is 'Title: Painpoint: Job title: email:'. 
                    Your job is to ensure that the generated cold emails are properly formatted and meet this requirement for a total of five emails.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            ##step_callback=streamlit_callback,
        )
