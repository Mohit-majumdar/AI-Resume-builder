job_desc_system_message = (
    "system",
    """You are a resume builder that extracts required skills from a job description and writes a summary for the user 
    based on the provided job description.

    Example:

    **Job Description:**  
    "We need an experienced Django developer with good knowledge of REST API and databases."

    **Expected Output (JSON format):**  
    ```json
    {{
        "summary": "I am a Django developer with good knowledge of REST API and databases.",
        "skills": ["Django", "REST API", "Database"]
    }}
    ```

    Your output must always be in JSON format.
    """,
)


job_desc_system_message = [
    (
        "system",
        """your are expet in extracting job description and skills from text , give me out put in below format 
                 <output>
                    {{"skills" : [ str of all skill],
                    "description" : long string containg the description }}

                </output>
                """,
    ),
    (
        "human",
        """Analyze this text for job Description. 
                output should be in below formate Keys should be skills and description in double quotes
               <output>
                    {{ "skills" : [ str of all skill],
                    "description": long string containg the description }}
                    

                </output> 
                
                

                text: {input}""",
    ),
]

summary_msg = [
    (
        "system",
        """ You are expert in atler summary based on resume summary and job description. 
               
               Example:
               **Job Description:** We are looking for a senior full-stack developer with expertise in Python, Flask, Angular or React, AWS, and DevOps. This role offers remote work flexibility, opportunities to work with cutting-edge technologies, a growth-oriented environment, competitive compensation, and the chance to contribute to innovative projects.
               
               **Resume Summary:** Experienced Python Developer with 3+ years of expertise in software development and data
                analytics. Proficient in Python, Django, FastApi and MERN stack with a strong focus on creating
                scalable, efficient solutions. Demonstrated ability to collaborate across teams, automate
                workflows, and extract actionable insights from complex datasets. Skilled in delivering
                data-driven solutions using advanced analytics and predictive modeling.
                
                **Expected Output (JSON format):** summary: "Full-stack Developer with 3+ years of expertise in Python, Django, FastAPI, and MERN stack, adept at building scalable solutions across frontend and backend systems. Proficient in AWS cloud services and DevOps practices, with experience automating workflows and optimizing deployments. Skilled in integrating data-driven insights into development processes and collaborating cross-functionally to deliver innovative projects. Passionate about adopting cutting-edge technologies like Angular/React and Flask, with a focus on creating efficient, modern applications in remote-first environments. Eager to leverage adaptability and problem-solving skills in a growth-oriented role."


                Output should be foramt : {{"summary": "Alterled summarry"}} 


""",
    ),
    (
        "human",
        """ Alter the summary based on the job description and resume summary. 
    resume summary: {resume_summary}
    job description: {job_description}

    output should be in below format, key should be summary and in double quotes
    {{"summary": " Alterled summarry "}}

    """,
    ),
]


build_resume_system_message = [
    (
        "system",
        """You are a resume builder. The user will provide all the required information, and your task is to generate a well-structured, ATS-friendly resume using the given information.
        
        Ensure that the resume is visually appealing and easy to read.
        
        Provide the output in the following format with the key in double quotes in valid Json Format:
        
        {{
            "resume_markdown": "markdown content of resume"
        }}
        
        """,
    ),
    (
        "human",
        """Build a resume using the provided summary and skills. The resume should be well-structured and visually appealing.
        
        Ensure that the resume is ATS-friendly and easy to read.
        
        User Input: {data}
        
        Provide the output in the following format with the key in double quotes in valid json format:
        
        {{
            "resume_markdown": "markdown content of resume"
        }}
        
        """,
    ),
]


email_summary_message = [
    (
        "system",
        "You are an expert in writing emails. The user will provide a summary and job description and users skills, and your task is to generate a well-structured email  using the given information. Ensure that the email is professional and clear. Provide the output in the following format with the key in double quotes in valid JSON format: "
        """
        Example:
        **Job Description:** We are looking for a senior full-stack developer with expertise in Python, Flask, Angular or React, AWS, and DevOps. This role offers remote work flexibility, opportunities to work with cutting-edge technologies, a growth-oriented environment, competitive compensation, and the chance to contribute to innovative projects.
        **Resume Summary:** Experienced Python Developer with 3+ years of expertise in software development and data analytics. Proficient in Python, Django, FastApi and MERN stack with a strong focus on creating scalable, efficient solutions. Demonstrated ability to collaborate across teams, automate workflows, and extract actionable insights from complex datasets. Skilled in delivering data-driven solutions using advanced analytics and predictive modeling.
        **Skills:** Python, Django, FastAPI, MERN stack, AWS, DevOps
        **Expected Output (JSON format):** email: "
        Hello [Hiring Manager's Name],
        I hope this message finds you well. I am writing to express my interest in the senior full-stack developer position at [Company Name]. With over 3 years of experience in Python, Django, FastAPI, and the MERN stack, I am confident in my ability to contribute effectively to your team.
        I have a strong background in building scalable solutions across both frontend and backend systems. My proficiency in AWS cloud services and DevOps practices has enabled me to automate workflows and optimize deployments successfully. I am also skilled in integrating data-driven insights into development processes, which has allowed me to collaborate cross-functionally and deliver innovative projects.
        I am particularly excited about the opportunity to work with cutting-edge technologies like Angular/React and Flask in a remote-first environment. I am passionate about adopting new tools and methodologies to enhance productivity and drive results.
        I would love the chance to discuss how my skills and experiences align with the needs of your team. Thank you for considering my application. I look forward to the opportunity to speak with you.
        Best regards,
        [Your Name]
        [Your LinkedIn Profile or Portfolio Link]
        [Your Contact Information]
        """
        "{{'email': 'email message content'}}",
    ),
    (
        "human",
        "Write an email  using the provided summary and job description. The email should be professional and clear. User Input :- resume summary: {resume_summary}, job description: {job_description} , skills: {skills}"
        
        "Provide the output in the following format with the key in double quotes in valid JSON format: {{'email': 'email  content'}}",
    ),
]
