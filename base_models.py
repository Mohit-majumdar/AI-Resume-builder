from dataclasses import dataclass
from enum import Enum
from abc import ABC,abstractmethod
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from decouple import config
import json
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser,PydanticOutputParser
import constants
import asyncio
from time import sleep

load_dotenv()

@dataclass
class LLMmodels(Enum):
    DEEPSEEK = "deepseek-r1:latest"
    OPENAI = "gpt-4"
    QWEN = "qwen2.5:latest"
    LLAMA = "llama3.2:latest"
    OpenRouterLLM = "deepseek/deepseek-r1:free"
    OpenRouterLLMLlama = "nvidia/llama-3.1-nemotron-70b-instruct:free"


class BaseModelClass(ABC):
    @abstractmethod
    def process_response(self,promt,build_resume=False,**kwarg):
        pass

class Deepseek(BaseModelClass):
    def __init__(self,model_name = LLMmodels.DEEPSEEK.value):
        self.models = ChatOllama(model=model_name,base_url=config("OLLAMA_BASE_URL",default="localhost"))

        super().__init__()

    @staticmethod
    def _clear_content(content,remove_think=True):
        if remove_think:
            res =  content.split("</think>")[-1]
        res = content
        json_data = res[res.find("{"):res.rfind("}")+1]
        print("json_data",json_data,type(json_data))
        json_res = json.loads(json_data)
        return json_res
    
    async def process_response(self,prompt,build_resume=False, **kwarg):
        
        chain = prompt | self.models
        content = chain.invoke(kwarg).content
        
        content = Deepseek._clear_content(content)
        return content
        

class OpenRouter(BaseModelClass):
    def __init__(self,model_name = LLMmodels.OpenRouterLLM.value):
    
        """
        Initialize the OpenRouter Model.

        Args:
            model_name (str): The model name to use. Defaults to LLMmodels.OpenRouterLLM.value.

        Attributes:
            _api_key (str): The API key to use for the OpenRouter API.
            model_name (str): The model name to use.
            models (ChatOpenAI): The ChatOpenAI model to use.
        """
        self._api_key = config("OPENAI_API_KEY")
        self.model_name = model_name

        self.models = ChatOpenAI(model=model_name,
                                 temperature=0.7,
                                 openai_api_key=self._api_key,
                                 openai_api_base=constants.OPENROUTER_API_BASE,
                                 )

        super().__init__()

    async def process_response(self,prompt,build_resume=False,**kwarg):

        if build_resume:
            class RsumeData(BaseModel):
                resume_markdown: str = Field(description="Resume in markdown format")

            parser = PydanticOutputParser(pydantic_object=RsumeData)
            chain = prompt | self.models | parser
            content =  chain.invoke(kwarg)
            print("content: ",content.dict())
            return content.dict()
        chain = prompt | self.models 
        
        content =  chain.invoke(kwarg).content
        if not content:
            sleep(20)
            content = chain.invoke(kwarg).content
        print("first_content: ",content)
        if "deepseek" in self.model_name:
            
            content = Deepseek._clear_content(content,remove_think=False)
            return content
        
            
        return content


class Qwen(BaseModelClass):
    def __init__(self):
        self.models = ChatOllama(model=LLMmodels.QWEN.value,base_url=config("OLLAMA_BASE_URL",default="localhost"))

        super().__init__()
    
    async def process_response(self, prompt,build_resume=False, **kwarg):
        class JobAnalysis(BaseModel):
                job_title: str = Field(description="Job title")
                skills: list[str] = Field(description="List of skills mentioned")
                description : str = Field(description="Full job description")
                confidence_score: int = Field(description="Confidence score 0-100")

        # 2. Create JSON parser with validation
        parser = JsonOutputParser(pydantic_object=JobAnalysis)

        chain = prompt | self.models | StrOutputParser| parser
        return chain.invoke(kwarg)

class OpenAI(BaseModelClass):
    def __init__(self):
        self.models = ChatOpenAI(model=LLMmodels.OPENAI.value,format="json")
        super().__init__()

    async def process_response(self,prompt,build_resume=False,**kwarg):
        chain = prompt | self.models
        return chain.invoke(kwarg)

class CreateLLM:
    @staticmethod
    def create_model(model_name):
        print(model_name)
        if model_name == LLMmodels.DEEPSEEK.name:
            
            return Deepseek()
        elif model_name == LLMmodels.OPENAI.name:
            pass
        elif model_name == LLMmodels.QWEN.name:
            return Qwen()        
        elif model_name == LLMmodels.LLAMA.name:
            pass
        elif model_name == LLMmodels.OpenRouterLLM.name:
            return OpenRouter()
        elif model_name == LLMmodels.OpenRouterLLMLlama.name:
            return OpenRouter(model_name=LLMmodels.OpenRouterLLMLlama.value)
        else:
            raise ValueError("Model not found")
 
        
    




