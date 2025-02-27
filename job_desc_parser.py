from langchain_ollama import ChatOllama
from pydantic import BaseModel,Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from system_messages import job_desc_system_message,resume_builder,html_system_msg
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class ResumeFormate(BaseModel):
    summary : str = Field(description="summary for resume showing experties of skill upto 100 words")
    skills: List[str] = Field(description="all the skills required for job role")


def chat_to_llm(desc,model_name,response_model:ResumeFormate):
    parser = PydanticOutputParser(pydantic_object=response_model)
    llm = ChatOllama(model=model_name,base_url="http://172.105.57.99")
    prompt = ChatPromptTemplate([
        job_desc_system_message,
        (
            "user",
            """this is the job description : {desc}"""
        )
    ]) 
    chain = prompt | llm | parser
    return chain.invoke({"desc":desc})


def build_resume(data, model_name):
    llm = ChatOllama(model=model_name,temperature=0,base_url="http://172.105.57.99")
    prompt = ChatPromptTemplate(
        [
            html_system_msg,
            (
                "user",
                "here are my summary: {summary} and skiils :{skills}"
            )
        ]
    )

    chain = prompt | llm 

    return chain.invoke({"summary":data.get("summary"),"skills":data.get("skills")})
if __name__ == "__main__":
    job_description = """
Job Title: - Data Engineer with Python + SQL
Location: -Indore
Exp- 3 years

Strong experience in Python scripting and SQL Knowledge is mandatory
Proficiency in Object Oriented and functional programming concepts
Programming experience in Python is desired however Java Ruby Scala Clojure are acceptable alternatives
Experience integrating services to build pipeline solutions In AWS Hadoop EMR Azure Google Cloud
AWS experience is a plus but not required
Nice to have experience with Relational and NoSQL databases
Nice to have DevOps or Data Ops experience
The Cognizant community:
We are a high caliber team who appreciate and support one another. Our people uphold an energetic, collaborative and inclusive workplace where everyone can thrive.

Cognizant is a global community with more than 350,000 associates around the world.
We don’t just dream of a better way – we make it happen.
We take care of our people, clients, company, communities and climate by doing what’s right.
We foster an innovative environment where you can build the career path that’s right for you.

"""

    model= "llama3.2:latest"
    res = chat_to_llm(job_description,model,ResumeFormate)
    data = res.model_dump()
    print(data)
    resume = build_resume(data,model)
    print(resume.content)