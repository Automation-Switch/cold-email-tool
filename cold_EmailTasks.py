from crewai import Task
from textwrap import dedent

class coldEmailTasks:

    def subniche(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f""" 
              Identify the companies subniche within {industry} specific to its industry and the services that {sender} that will be beneficial to the job titles within the various companies. 
              Using information provided by a business analyst, identify specific companies and subniches of {industry} and the broader industry at large.
              This task involves analyzing the company's operations, comparing it with the broader industry, and using business analyst insights to pinpoint specialized areas. 
              The final output should include services offered by {sender}, a detailed report on the identified companies and their subniches, 
              focusing on unique products or services, market segmentation, technological innovations, and customer needs.
            {self.__tip_section()}
          """),
            expected_output="A comprehensive detail of the pain points of Job Titles and their companies should be provided by the Business Portfolio Analyst.",
            #output_file = "Companies.md",
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
            output_file = "Job Titles.md",
            agent=agent)

    def painPoints(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Identify pain points of Job Titles provided by the Business Portfolio Analyst. These pain points should be ranked in order of the intensity of the impact on revenue. 
              Filter the pain points and identify the solutions that were used to address them. You based your ranking on reviews and sentiments from the targeted Job Titles within {industry}.
              Expand this analysis into a comprehensive report with a detailed per-step plan, including identification, ranking, filtering, and solution identification.
              You MUST identify specific pain points, rank them by impact on revenue, filter them to highlight the most critical ones, and suggest actual solutions used to address these pain points.
              This report should cover all aspects of the analysis, from initial identification to final solutions, integrating insights from the Business Portfolio Analyst with practical business impacts.
              Your final answer MUST be a complete expanded report, formatted as markdown, encompassing each step of the process, detailed explanations of pain points, their rankings, 
              identified solutions, and reasons for selecting each solution, ensuring the most thorough understanding of the issues and resolutions. 
              Be specific and explain why each pain point and solution was chosen, and what makes them significant!
              {self.__tip_section()}
          """),
            expected_output="A comprehensive detail of the pain points of Job Titles provided by the Business Portfolio Analyst.",
            output_file = "Pain Points.md",
            agent=agent)
    
    def coldEmailWriter(self, agent, industry, sender, briefDes ,offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Generate cold emails in less than 100 words for the various Job Titles provided by the Business Portfolio Analyst. 
              Explain at the end of each email how you came by these emails, including the processes and steps taken.
              Mention that our {sender} has specifically helped a similar company that struggled with the same problem in the past. 
              Additionally, include how {sender} can address their pain points with modern solutions.
              You are a cold email writer who takes into account the information and details provided by the Business Analyst, 
              the Business Portfolio Analyst, and the Business Pain Points Analyst.
              {self.__tip_section()}
          """),
            expected_output="The final must be well-formatted Cold emails for the various Job Titles and their companies provided by Business Portfolio Analyst.",
            agent=agent)

    def coldEmailReviewer(self, agent, industry, sender, briefDes ,offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Review the cold emails generated by the Cold Email Generator to ensure they follow the required format: 'Title: Painpoint: Job title: email: where email is not the email address but the cold email'. 
              Make sure that the format is strictly adhered to for a total of five emails. 
              If there are any deviations from the format, provide detailed feedback on what needs to be corrected.
              The task involves carefully checking each email to ensure that it meets the format requirements and that the content is clear and properly structured.
              The final output should include feedback on the email format adherence and any necessary corrections.
              {self.__tip_section()}
          """),
            expected_output="Five cold emails, that adhere to the format 'Title: Painpoint: Job title: email:'.",
            output_file = "Cold Emails.md",
            agent=agent)

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"
