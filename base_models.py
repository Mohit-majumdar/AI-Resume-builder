from dataclasses import dataclass
from enum import Enum
from abc import ABC,abstractmethod
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from decouple import config
import json
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import constants

load_dotenv()

@dataclass
class LLMmodels(Enum):
    DEEPSEEK = "deepseek-r1:latest"
    OPENAI = "gpt-4"
    QWEN = "qwen2.5:latest"
    LLAMA = "llama3.2:latest"
    OpenRouterLLM = "deepseek/deepseek-r1:free"


class BaseModelClass(ABC):
    @abstractmethod
    def process_response(self,promt):
        pass

class Deepseek(BaseModelClass):
    def __init__(self):
        self.models = ChatOllama(model=LLMmodels.DEEPSEEK.value,base_url=config("OLLAMA_BASE_URL",default="localhost"))

        super().__init__()

    @staticmethod
    def _clear_content(content):
        res =  content.split("</think>")[-1]
        json_data = res[res.find("{"):res.rfind("}")+1]
        print(json_data,type(json_data))
        json_res = json.loads(json_data)
        return json_res
    
    def process_response(self,prompt,**kwarg):
        
        chain = prompt | self.models
        content = chain.invoke(kwarg).content
        content = Deepseek._clear_content(content)
        return content
        

class OpenRouter(BaseModelClass):
    def __init__(self):
    
        self._api_key = config("OPENAI_API_KEY")

        self.models = ChatOpenAI(model=LLMmodels.OpenRouterLLM.value,
                                 temperature=0.7,
                                 openai_api_key=self._api_key,
                                 openai_api_base=constants.OPENROUTER_API_BASE,
                                 )

        super().__init__()

    def process_response(self,prompt,**kwarg):
        chain = prompt | self.models
        
        content =  chain.invoke(kwarg).content
        if not content:
            content = chain.invoke(kwarg).content
        print("first_content: ",content)
        if "deepseek" in LLMmodels.OpenRouterLLM.value:
            content = Deepseek._clear_content(content)
        return content


class Qwen(BaseModelClass):
    def __init__(self):
        self.models = ChatOllama(model=LLMmodels.QWEN.value,base_url=config("OLLAMA_BASE_URL",default="localhost"))

        super().__init__()
    
    def process_response(self, prompt,**kwarg):
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

    def process_response(self,prompt,**kwarg):
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
        else:
            raise ValueError("Model not found")
 
        
    




