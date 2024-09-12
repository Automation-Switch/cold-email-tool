import os
from crewai import Agent
from langchain_community.chat_models import ChatCohere
from langchain_openai import OpenAI
from langchain_groq import ChatGroq
from tools.search_tools import SearchTools
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
cohere_api_key = os.environ.get("COHERE_API_KEY")  
groq_api_key = os.environ.get("GROQ_API_KEY")

# Cold Email Agents Class

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
    def __init__(self, llm_name):
        # Initialize available LLMs
        self.llm_dict = {
            "cohere": ChatCohere(cohere_api_key="ieLPQ8jIDR7czKpyAcRYPJTdjjP27AAVwR7Gvwzs"),
            "openai": OpenAI(api_key=openai_api_key),
            "groq": ChatGroq(
                temperature=0,
                groq_api_key=groq_api_key,
                model_name="mixtral-8x7b-32768"
            )
        }
        # Set the selected LLM
        if llm_name in self.llm_dict:
            self.llm = self.llm_dict[llm_name]
        else:
            raise ValueError(f"LLM '{llm_name}' not recognized. Choose from {', '.join(self.llm_dict.keys())}.")

    def business_analyst_agent(self):
        return Agent(
            role='Business Analyst',
            goal="Identify the companies and subniches within {industry}.",
            backstory="""You are a business analyst, and your primary function is to identify companies/businesses and their specific subniches
                    within {industry} and the broader industry at large. Additionally, you need to assess the services that {sender} offers which will be beneficial to companies within {industry}.
                    With this information, you aid businesses in targeting precise market segments. You collect information from {offer_pdf}, {briefDes} or {offer_link}, {industry}, {sender}.
                    Armed with these details, conduct thorough research on the current companies and subniches within {industry} and the services that {sender} offers that will be beneficial to the companies identified.""",
            # tools=[
            #     SearchTools.search_internet,
            # ],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  # Use the selected LLM here
            #tep_callback=streamlit_callback
        )

    def business_portfolio_analyst(self):
        return Agent(
            role='Business Portfolio Analyst',
            goal="""Identify and list the companies and Job Titles within {industry} that are responsible for or will benefit from {offer_link} or {offer_pdf}, 
            and the supervisor in charge of the Job Titles.""",
            backstory="""You are a Business Portfolio Analyst that identifies relevant companies and job titles within {industry}
                    that would benefit from {offer_link}, {briefDes}, or {offer_pdf}. You analyze information from the Business Analyst and based on its output, make this decision.
                    Your mission is to enhance cold email campaigns by targeting Job Titles and the key decision makers of these Job titles who are the final decision-makers.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  
            #step_callback=streamlit_callback
        )

    def idealCustomer_profiler(self):
        return Agent(
            role='Customer Insight Analyst',
            goal="""Identify and provide an ideal customer profile  of the job titles and companies identified by the business portfolio analyst. 
                    The ICP should include detailed insights that help in targeting and understanding the best potential customers for the {briefDes} service
                    being offered by the user. This should include detailed insights that help in targeting and understanding
                    the best potential customers for a product or service within the industry.""",

            backstory="""You are a renowned customer insight analyst firm Nielsen with extensive knowledge
                         in audience insights, data and analytics,and shapes the future of businesses with accurate measurement of what people listen, buy or
                         show interest within. You also understand and provide that an ideal customer profile is a detailed description of the
                         type of customer and their companies provided by the business portfolio analyst, and the ones that are most likely to benefit from
                         and be interested in the {briefDes} provided by the user. Your role is to make the process of
                         identifying and targeting these profiles more efficient by focusting on industry-specific characteristics.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm, 
        )

    def cold_email_generator(self):
        return Agent(
            role='Cold Email Generator',
            goal="""Generate cold emails in less than 100 words for the various Job Titles within the companies listed provided by the Business Portfolio Analyst.""",
            backstory="""You are a world class marketer  who has the expertise of marketing expert Russel Brunson and Direct marketing expert and strategist Dan Kennedy. You take into account the information and details provided by the Business Analyst, the Business Portfolio Analyst,
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
            llm=self.llm,  # Use the selected LLM here
            #step_callback=streamlit_callback
        )

    def cold_email_reviewer_agent(self):
        return Agent(
            role='Cold Email Reviewer',
            goal="""Review the generated cold emails to ensure they follow the format: 'Title: Painpoint: Job title: email:' for a total of five emails.""",
            backstory="""You are sales and marketing expert and your niche area of expertise is cold sales emails creation. You posess world class ability in identifying cold email copy that converts. You are responsible for reviewing all cold  sales emails to ensure they adhere to a specific format. This format is 'Title: Painpoint: Job title: email:'. 
                    Your job is to ensure that the generated cold sales emails are properly formatted and meet this requirement for a total of five emails.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  # Use the selected LLM here
            #step_callback=streamlit_callback
        )
