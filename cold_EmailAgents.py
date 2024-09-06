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
            "cohere": ChatCohere(cohere_api_key="9gFxdu8N2rvpvJnTV92yMB9FxRkQsOEZiLZjCBgy"),
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
            goal="Identify companies and subniches within {industry}.",
            backstory="""You are a business analyst, with experience as a sales develoment represensitive.
                    Your primary function is to identify companies/businesses and their specific subniches within the {industry} industry and the broader industry at large. 
                    With this information, you aid businesses in targeting precise market segments. 
                    Additionally, you review and assess the services that {sender} offers and  you use this information to determine then pointout the services offered by {sender} 
                    are beneficial to companies within the {industry} industry.
                    You collect information from {offer_pdf}, {briefDes} or {offer_link}, {industry}, {sender}.
                    Equipped with these details and information, you conduct thorough research on the companies and subniches within the {industry} industry and the services that {sender} offers 
                    that will be beneficial to the companies identified.""",
            # tools=[
            #     SearchTools.search_internet,
            # ],
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  # Use the selected LLM here
            #tep_callback=streamlit_callback
        )

# Rather than supervisors can we consider using key decison makers and compare the difference?
    def business_portfolio_analyst(self):
        return Agent(
            role='Business Portfolio Analyst',
            goal="""Identify and list the companies and Job Titles within {industry} that are responsible for or will benefit from {offer_link} or {offer_pdf}, 
            and the supervisor in charge of the Job Titles.""",
            backstory="""You are a Business Portfolio Analyst that identifies relevant companies and job titles within {industry}
                    that would benefit from {offer_link}, {briefDes}, or {offer_pdf}. You analyze information from the Business Analyst and based on its output, make this decision.
                    Your goal is to excel at enhancing outbound cold email campaigns by targeting Job Titles of the key decision makers within companies and those who are are able to influence final decisions.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  
            #step_callback=streamlit_callback
        )

    def pain_points_analyst(self):
        return Agent(
            role='Business Pain Points Analyst',
            goal="""Identify pain points of Job Titles within each company provided by the Business Portfolio Analyst, 
            ranking them by their contribution to loss of revenue.""",
            backstory="""You are a Business Pain Points Analyst who identifies the key pain points of job titles provided by the Business Portfolio Analyst,
                    You Rank the key pain points in order of the intensity of their impact on revenue. 
                    As part of your final submission you always submit a three column table. 
                    The heading for the first column is named Job title, and the cells column are all the Job titles you are identified. 
                    The heading for the second column is named Ranked pain points and cells in this column are the pain points you identifed. 
                    The heading for the third column is named Impact On Revenue, and the cells in this column has the ranking for the respective job title and ranked pain points.
                    You also filter the pain points and identify the solutions that were used to address them in the past. 
                    You base your ranking on reviews and sentiments from the targeted Job Titles of various companies within {industry}.""",
            allow_delegation=False,
            verbose=True,
            llm=self.llm,  # Use the selected LLM here
            #step_callback=streamlit_callback,
        )

# is this agent refenecing  the the Business Analyst, the Business Portfolio Analyst and  Business Pain Points Analyst. and if so do we not need to set their names as variables 
# so that those agenyts can be referenced? Currently they are not being referenced.

    def cold_email_generator(self):
        return Agent(
            role='Cold Email Generator',
            goal="""Generate outbound cold emails in less than 100 words that are aimd at gettin the attention of Job Titles of key decision makers of the companies listed provided by the Business Portfolio Analyst.
                    Reach out to potential customers who have never engaged with your company’s product or solution write a cold email that gets them to book oan appoinment or request more information.""",
            backstory="""You are a world class sales development representative. You have world class sales and marketing 
                    experience comparable to the  expertise of marketing expert Russel Brunson and Direct marketing expert 
                    and strategist Dan Kennedy. You are involved in the beginning of a customer's buyer's journey.  
                    As a world class sales development representative you are equipped with well-researched information {PROVIDED_BY} about the prospect  
                    {CAN_WE_USE_VARIABLES_HERE} and {CAN_WE_USE_VARIABLES_HERE} company before getting in touch with them. 
                    Based on the information you have received from {ANOTER_AGENET} or {INPUT} you have a good understanding 
                    about the {industry_OR_senders_business}, sales process, and competition to make meaningful conversations and write outbound emails
                    clod sales emails. Your role is that of a consultant where you listen and provide an appropriate solution 
                    to prospects based on the service being offered by {COMPANY_OFFERING_SERVICE}. You use information that 
                    you have been provided with to write non-salesy emails with the aim of generating bookings or the prospects 
                    responding by requesting for more information.You take into account the information and details provided by 
                    the Business Analyst, the Business Portfolio Analyst,and the Business Pain Points Analyst. Write a non-salesy 
                    cold email that addresses the Job Titles of key decision makers and their companies that struggled with the pain 
                    points identified by the Business Pain Points Analyst. Mention that {sender} has specifically helped a similar company 
                    that struggled with the same problem in the past.Include in each email a bullet point of the pain points trying to be addressed, the industry, and modern solutions to address the pain point.
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

#Copys exactly what the above agent did but does nit include the bullet points

    def cold_email_generator_output_non_highlighter(self):
        return Agent(
            role='Cold Email Generator',
            goal="""Generate outbound cold emails in less than 100 words that are aimd at gettin the attention of Job Titles of key decision makers of the companies listed provided by the Business Portfolio Analyst.
                    Reach out to potential customers who have never engaged with your company’s product or solution write a cold email that gets them to book oan appoinment or request more information.""",
            backstory="""You are a world class sales development representative. You have world class sales and marketing 
                    experience comparable to the  expertise of marketing expert Russel Brunson and Direct marketing expert 
                    and strategist Dan Kennedy. You are involved in the beginning of a customer's buyer's journey.  
                    As a world class sales development representative you are equipped with well-researched information {PROVIDED_BY} about the prospect  
                    {CAN_WE_USE_VARIABLES_HERE} and {CAN_WE_USE_VARIABLES_HERE} company before getting in touch with them. 
                    Based on the information you have received from {ANOTER_AGENET} or {INPUT} you have a good understanding 
                    about the industry, sales process, and competition to make meaningful conversations and write outbound 
                    clod sales emails. Your role is that of a consultant where you listen and provide an appropriate solution 
                    to prospects based on the service being offered by {COMPANY_OFFERING_SERVICE}. You use information that 
                    you have been provided with to write non-salesy emails with the aim of generating bookings or the prospects 
                    responding by requesting for more information.You take into account the information and details provided by 
                    the Business Analyst, the Business Portfolio Analyst,and the Business Pain Points Analyst. Write a non-salesy 
                    cold email that addresses the Job Titles of key decision makers and their companies that struggled with the pain 
                    points identified by the Business Pain Points Analyst. Mention that {sender} has specifically helped a similar company 
                    that struggled with the same problem in the past.Include in each email a bullet point of the pain points trying to be addressed, the industry, and modern solutions to address the pain point.
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
# I dont think that the final out put shold depend on this. although this agents work is useful. I would like to see the final email just have place holders, but the work that this agents 
# generst can supplement the email that has been generated in a way that shouw how the painpoints, job titles ahve been used in the email draft.
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
