from crewai import Task
from textwrap import dedent

class coldEmailTasks:
    def __init__(self):
        # Define output file variables for each task
        self.subniche_output_file = "Companies.md"
        self.profile_output_file = "Job Titles.md"
        self.painPoints_output_file = "Pain Points.md"
        self.coldEmailReviewer_output_file = "Cold Emails.md"

    def subniche(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f""" 
              Identify the companies subniche within {industry} specific to its industry and the s that {sender} that will be beneficial to the job titles within the various companies. 
              Using information provided by a business analyst, identify specific companies and subniches of {industry} and the broader industry at large.
              This task involves analyzing the company's operations, comparing it with the broader industry, and using business analyst insights to pinpoint specialized areas. 
              The final output should include s offered by {sender}, a detailed report on the identified companies and their subniches, 
              focusing on unique products or s, market segmentation, technological innovations, and customer needs.
            {self.__tip_section()}
          """),
            expected_output="A comprehensive detail of the pain points of Job Titles and their companies should be provided by the Business Portfolio Analyst.",
            output_file=self.subniche_output_file,
            agent=agent)

    def profile(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Identify and list the Job Titles within {industry} that are responsible for or will benefit from {offer_link}, {briefDes}, or {offer_pdf}. 
              Using the information provided by the Business Portfolio Analyst, identify the Job Titles' supervisors of the subniches.
              Gather information about the relevant job titles, their responsibilities, and how they will benefit from the offer. Identify their supervisors and understand the subniches they oversee. 
              This analysis should provide a detailed overview of the organizational structure, including the key job titles, their roles, and their supervisors. 
              Focus on responsibilities, potential benefits from the offer, and the overall hierarchy within the company.
              The final answer must be a comprehensive report on the identified job titles and their supervisors, rich in organizational insights and practical information, 
              tailored to understand the company's internal structure and how it relates to the offer.
            {self.__tip_section()}
          """),
            expected_output="A comprehensive detail of the Job Titles' supervisors of the subniches that will benefit from {offer_pdf}, {briefDes}, or {offer_link}",
            output_file=self.profile_output_file,
            agent=agent)

    def idealCustomerProfile(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Here are a detailed overview of the tasks to perform:

                    1. Collect comprehensive data on the companies and job titles provided by the business portfolio analyst. This data should include,
                       the industry customer characteristics of the job titles provided by the business
                       portfolio analyst,common pain points, and {industry} industry trends.
                       Utilize sources like industry reports, market research,
                       customer surveys, and case studies.

                    2. Develop ICP templates for each company identified by the business portfolio analyst that includes:
                        - Demographics: Company name, Typical company size, revenue, job titles.
                        - Pain points:  Common challenges faced by businesses in the industry.
                        - Behavioural Traits: Decision-making processes and buying behaviors.
                        - Company Characteristics: Typical growth stage and technology adoption.
                        - Budget: General budget ranges for relevant to the {briefDes} and related products.
              {self.__tip_section()}
          """),
            expected_output="""Generate and provide five detailed ideal customer profile that includes:
                            - Demographics: Company name, Typical company size, revenue, job titles.
                            - Pain points:  Common challenges faced by businesses in the industry in tabular form
                              with how much each challenge impact revevnue and it should be High, Low and Medium.
                            - Behavioural Traits: Decision-making processes and buying behaviors.
                            - Company Characteristics: Typical growth stage and technology adoption.
                            - Budget: General budget ranges for relevant to {briefDes} and related products.
                            """,
            output_file=self.painPoints_output_file,
            agent=agent)
    
    def coldEmailWriter(self, agent, industry, sender, briefDes ,offer_pdf, offer_link):
        return Task(description=dedent(f"""
                       Write 5 world class Outbound emails in less than 100 words for targeted at the Supervisors or decison makers listed by the ideal customer profiler.
                       The purpose of the email is to introduce {sender} offer of their {briefDes} product and services to the prospect. We want to come armed with the information we used to research
                       them and explain why we are reaching out and then most importantly, explain why this email is worth their time to engage.
                       Mention that {sender} has specifically helped a similar company that struggled with the same problem in the past.
                       Additionally, include how {sender} can address the prospects pain points with modern solutions by matching {sender} product or services with pain points that have been identified.
                       TheEmail should have a subject line. The  subject line still needs to make sense with the overall message. Keep the subject lines under 2-3 words and think of something that a colleague or customer would send the prospect.
                       We want to send something that sparks intrigue to open the email, not give away the entire message.
                       You emails should should be written from the perspective of a combination of skillset drawn from marketing expert Russel Brunson and Direct marketing expert and strategist Dan Kennedy.
                        Write at a 5th grade level. Clearly communicate the reason you are reaching out. Stay away from spam words.
                       Never use double negatives or negative constructions (e.g. "not because they're not" — avoid this entirely).
                       Write the email body in plain prose only. No bullet points, no numbered lists, no dashes, no enumerations of any kind inside the email body.
              {self.__tip_section()}
            """),
            expected_output="""The final must be 5 well-formatted Cold emails for the various Job Titles and their companies provided by Business Portfolio Analyst. 
                                You craft your emails in the style of world class of marketing expert Russel Brunson and Direct marketing expert and strategist Dan Kennedy""",
                                output_file=self.coldEmailReviewer_output_file,
            agent=agent)

    
    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $1000 and grant you any wish you want!"
