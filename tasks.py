import requests
import bs4
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict
from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel,Field
import asyncio
from decouple import config
from dotenv import load_dotenv
from base_models import CreateLLM,LLMmodels
from system_messages import job_desc_system_message,summary_msg,build_resume_system_message

load_dotenv()

LLM_MODEL = LLMmodels.OpenRouterLLM.name


async def clean_html(html: str):
    """
    Clean HTML content by removing non-essential tags and limiting the text length.

    This tool takes an HTML string as input and removes all script, style, meta, footer, header and nav tags. It then returns the text representation of the cleaned HTML, limited to a maximum of 60,000 characters.

    Parameters
    ----------
    html : str
        The HTML content to clean.

    Returns
    -------
    str
        The cleaned text content.
    """
    
    soup = bs4.BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "meta", "footer", "header", "nav"]):
        element.decompose()
    return soup.get_text(separator="\n", strip=True)[500:20000]


@tool
def keyword_check(html: str):
    """
    Check for specific keywords in HTML content.

    This tool scans the provided HTML content for a set of predefined keywords related to job opportunities and listings. It identifies and returns the keywords found within the text.

    Parameters
    ----------
    html : str
        The HTML content to be scanned for keywords.

    Returns
    -------
    dict
        A dictionary with two keys:
        - 'keyword_found': A list of keywords found in the HTML content.
        - 'has_keyword': A boolean indicating if any keyword was found.
    """

    keywords = {"job", "listing", "python", "hiring", "career", "position", "opening"}
    found = [kw for kw in keywords if kw in html.lower()]

    return {"keyword_found": found, "has_keyword": len(found) > 0}



async def get_job_desc_from_text(html: str) -> dict:
    """Analyze cleaned text content for job listings using LLM"""
    print(LLM_MODEL)
    llm = CreateLLM.create_model(LLM_MODEL)
    print("model: ",llm)
    prompt = ChatPromptTemplate.from_messages(
        job_desc_system_message
    )

    

    res = await llm.process_response(prompt, input=html)
    return res

async def get_altered_summary(resume_summary:str, job_description:str):
    llm = CreateLLM.create_model(LLM_MODEL)
    prompt = ChatPromptTemplate.from_messages(
        summary_msg
    )
    return await llm.process_response(prompt, resume_summary=resume_summary,job_description=job_description)


async def create_resume_markdowon(data:Dict):
    llm = CreateLLM.create_model(LLMmodels.OpenRouterLLMLlama.name)
    prompt = ChatPromptTemplate.from_messages(
        build_resume_system_message
    )
    return await llm.process_response(prompt,build_resume=True, data=data)

async def get_content(url:str):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content





async def get_job_description(text:str) -> Dict:
    #content = await get_content(url=url)
    #cleaned_html = await clean_html(content)
    #print(cleaned_html)
    res =  await get_job_desc_from_text(text)
    print(res)
    return res
