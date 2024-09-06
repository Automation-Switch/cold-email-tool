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
              Identify the companies subniche within {industry} specific to its industry and the services that {sender} that will be beneficial to the job titles within the various companies. 
              Using information provided by a business analyst, identify specific companies and subniches of {industry} and the broader industry at large.
              This task involves analyzing the company's operations, comparing it with the broader industry, and using business analyst insights to pinpoint specialized areas. 
              The final output should include services offered by {sender}, a detailed report on the identified companies and their subniches, 
              focusing on unique products or services, market segmentation, technological innovations, and customer needs.
            {self.__tip_section()}
          """),
            expected_output="A comprehensive detail of the pain points of Job Titles and their companies should be provided by the Business Portfolio Analyst.",
            output_file=self.subniche_output_file,
            agent=agent)

    def profile(self, agent, industry, sender, briefDes, offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Identify and list the Job Titles within {industry} that are responsible for or will benefit from {offer_link}, {briefDes}, or {offer_pdf}. 
              Using the information provided by the Business Portfolio Analyst, identify the Job Titles' of decision makers and supervisors of the subniches.
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
            expected_output="""A comprehensive detail of the pain points of Job Titles provided by the Business Portfolio Analyst. You Rank the key pain 
                    points in order of the intensity of their impact on revenue. As part of your final submission you always submit a three column table. 
                    The heading for the first column is named Job title, and the cells column are  all the Job titles you are identified. The heading for the second 
                    column  is named Ranked pain points and  cells in this column are the pain points you identifed. The heading for the third column is named 
                    Impact On Revenue, and the cells in this column has the ranking for the respective  job title and ranked pain points.""",
            output_file=self.painPoints_output_file,
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
            expected_output="""The final must be well-formatted Cold emails for the various Job Titles and their companies provided by Business Portfolio Analyst. 
                                You crafted your emails in the style of world class of marketing expert Russel Brunson and Direct marketing expert and strategist Dan Kennedy""",
            agent=agent)
    


    #NEW
    def coldEmailWriter_B(self, agent, industry, sender, briefDes ,offer_pdf, offer_link):
        return Task(description=dedent(f"""
              Generate emails in less than 100 words for the various Job Titles provided by the Business Portfolio Analyst.
              The purpose of email the email is to introduce our offer to the prospect. We want to come armed with the information we used to research
              them and explain why we are reaching out and then most importantly, explain why this email is worth their time to engage. 
              Mention that {sender} has specifically helped a similar company that struggled with the same problem in the past. 
              Additionally, include how {sender} can address the prospects pain points with modern solutions by matching {sender} product or services with  pain points that have been identified.
              You are a sales development represensitive who is responsible for contacting potential prospects through cold emails, Identifying prospect's needs and suggesting appropriate 
              products/services. You present the {sender} company to potential prospects via cold outbound email while takeing into account the information and details provided by the Business Analyst, 
              the Business Portfolio Analyst, and the Business Pain Points Analyst.
              {self.__tip_section()}
          """),
            expected_output="""Outbound Cold emails for the various Job Titles and their companies provided by Business Portfolio Analyst. 
                              The subject for the email lines that suggest or infer it's possible a colleague or a customer has sent them the email WITHOUT LYING.
                              The subject line still needs to make sense with the overall message. Keep your subject lines under 2-3 words and think of something that a colleague or customer would send the prospect.
                              We want to send something that sparks intrigue to open the email, not give away the entire message. 
                              You emails should should be written from the perspective of a combination experience drawn from marketing expert Russel Brunson and Direct marketing expert and strategist Dan Kennedy.
                              Write at a 5th grade level. Clearly communicate the reason you are reaching out. Stay away from spam words. Keep the email shorter than 100 words. 
                              {{first_name}} {{Lead with the sentence explaining why we are reaching out to them and what research we have done. Answer the “why you, why now?” question.}}
                              As part of the final email framework, ask a question that cuts through to our prospect's problems whether they know it or not to make them know about how they are solving 
                              their current problem OR segue with that homework into how we can help.
                              include a call to action. The Call to action should seek to answer the question “How do we make this worth this prospects time?”
""",
            agent=agent)
    
    


    # The final could probbaly be broken into two parts, we want the tool to simpley generate the 
    # email with using bullet points to identify  Title: Painpoint: Job title etc. The final email should suffice
    # we can then supplement it by presenting a sepereate email witout the hilighte pain point tiltles etc

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
            output_file=self.coldEmailReviewer_output_file,
            agent=agent)

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"
    

