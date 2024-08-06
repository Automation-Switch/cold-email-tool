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
                             about given topic and return relevant results
                             Use the following format:
                             Thought: you should always think about what to do
                             Action: the action to take, only one name of [Search the internet], just the name, exactly as it's written.
                             Action Input: the input to the action, just a simple a python dictionary using " to wrap keys and values.Observation: the result of the action
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



class ColdEmailAgents():

    def __init__(self):
     self.llm = ChatGroq(
        temperature = 0,
        groq_api_key=st.secrets['GROQ_API_KEY'],
        model_name="llama3-70b-8192",
    )

    def business_analyst_agent(self):
        return Agent(
            role='Business Analyst',
            goal="Identify the companies and subniches within {industry}.",
            backstory="""You are a business analyst and your primary function is to identify companies/businesses and their specific subniches,
                    of {industry} and the broader industry at large and also the services that {sender} offers which will be beneficial to companies within {industry}. With this information, you aid businesses in targeting precise market segments. 
                    You collect information from {offer_pdf}, {briefDes} or {offer_link}, {industry}, {sender} and. Armed with these details, 
                    conduct thorough research on the current companies and subniches within {industry} and the services that {sender} offers that will be beneficial to the companies identified.""",
            tools=[
                SearchTools.search_internet,
            ],
            allow_delegation= False,
            verbose=True,
            llm = self.llm,
            ##step_callback=streamlit_callback,
        )

    def business_portfolio_analyst(self):
        return Agent(
            role='Business Portfolio Analyst',
            goal="""Identify and list the companies and Job Titles within {industries} that are responsible for or will benefit from{offer_link} or {offer_pdf}, 
            and the supervisor in charge of the Job Titles.""",
            backstory= """You are a Business Portfolio Analyst that identifies relevant companies job titltes within {industry},
                    that would benefit from {offer_link}, {briefDes} or {offer_pdf}. You analyse information from Business Analyst and based on its output, make this decision.
                    Your mission is to enhance cold campaigns by targeting Job Titles and supervisor to these Job titles that are the final decision makers.""",
    
            allow_delegation= False,
            verbose=True,
            llm = self.llm,
            #step_callback=streamlit_callback,
        )

    def pain_points_analyst(self):
        return Agent(
            role='Business Pain Points Analyst',
            goal="""Identify pain points of Job Titles within each company provided by the Business Portfolio Analyst, 
            ranking them from the one that contributes to loss of revenue.""",
            backstory="""You are Business Pain Points Analyst that identifies the key pain points of Job titles provided by Business Portfolio Analyst,
                    ranking the key pain points in order of the intensity of the impact on revenue.
                    You also filter the pain points and identify the solutions that were used to address them,
                    in the past. You based your ranking based on reviews and setiments from the targeted Job Titles of various companies within {industry}.""",
        
            allow_delegation= False,
            verbose=True,
            llm = self.llm,
            step_callback=streamlit_callback,
        )
    
    def cold_email_generator(self):
        return Agent(
            role='Cold Email Generator',
            goal=""" Generate cold emails in less than 100 words for the various Job Titles within the companies listed provided by Business Portfolio Analyst.""",
            backstory=""" You are a cold email writer that takes into account the information and details provided by the Business Analyst, the Business Portfolio Analyst,
                    "and the Business Pain Points Analyst. Write a non salesy cold email that addresses the Job titles and their companies that struggled with the pain ponts identified by the Business Pain Points Analyst. 
                    "Mention that our {sender} has specifically  helped a similar company  that struggled with the same problem in the past.
                    Include in each mail how a bullet of the pain points trying to address, the industry and modern solutions to address the pain point
                    Using this as a template:
                    Pain point:
                    Company: 
                    Industry:
                    Modern Solution:
                    Cold Email:""",
            
            allow_delegation= False,
            verbose=True,
            llm = self.llm,
            step_callback=streamlit_callback,
        )
