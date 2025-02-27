from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Initialize DeepSeek Model
chat = ChatOllama(
   model="deepseek-r1:1.5b"
)

# Define Desired Output Structure
class BlogPost(BaseModel):
    title: str = Field(description="Title of the blog post")
    summary: str = Field(description="1-sentence summary")
    tags: list[str] = Field(description="Relevant tags")
    word_count: int = Field(description="Estimated word count")

# Set Up Parser and Prompt
parser = PydanticOutputParser(pydantic_object=BlogPost)

prompt = ChatPromptTemplate.from_template(
    """Generate a blog post about {topic} following this format:
{format_instructions}

Topic: {topic}"""
)

# Create Chain
chain = prompt | chat | parser

# Invoke with Example Topic
try:
    result = chain.invoke({
        "topic": "AI in healthcare",
        "format_instructions": parser.get_format_instructions()
    })
    print("Structured Output:")
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary}")
    print(f"Tags: {', '.join(result.tags)}")
    print(f"Word Count: {result.word_count}")
except Exception as e:
    print(f"Error: {str(e)}")