from transformers import AutoTokenizer,AutoModel
import markdown
from weasyprint import HTML
import fitz
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio
import re
class ResumeRag:
    def __init__(self,model_name = "sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.resume_data = []
        self.embadings = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = asyncio.Lock()

    @staticmethod
    async def clean_markdown(markdown_text):
        text = re.sub(r'["""]', '"', markdown_text)
        text = re.sub(r"[''']", "'", text)
    
        # Ensure proper spacing after list markers
        text = re.sub(r'^\s*[-*+](?!\s)', r'- ', text, flags=re.MULTILINE)
        
        # Ensure headers have space after #
        text = re.sub(r'(^|\n)(#+)([^#\s])', r'\1\2 \3', text)
        
        # Remove any complex formatting that might confuse ATS
        text = re.sub(r'{.*?}', '', text)
        
        return text
    @staticmethod
    async def markdown_to_pdf(markdown_text,file_path):
        clened_markdown = await ResumeRag.clean_markdown(markdown_text)
        html_text = markdown.markdown(clened_markdown)

        html_template = f"""
            <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ 
                            font-family: Arial, Helvetica, sans-serif;
                            line-height: 1.5;
                            margin: 10px; 
                            font-size: 11pt;
                            color: #000000;
                        }}
                        h1, h2, h3, h4, h5, h6 {{ 
                            font-family: Arial, Helvetica, sans-serif;
                            margin-top: 12pt;
                            margin-bottom: 6pt;
                            font-weight: bold;
                            color: #000000;
                        }}
                        h1 {{ font-size: 16pt; }}
                        h2 {{ font-size: 14pt; }}
                        h3 {{ font-size: 12pt; }}
                        p {{ margin-bottom: 8pt; }}
                        ul, ol {{ margin-top: 0; margin-bottom: 8pt; }}
                        li {{ margin-bottom: 4pt; }}
                        a {{ color: #000000; text-decoration: none; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 12pt; }}
                        th, td {{ 
                            text-align: left; 
                            padding: 4pt; 
                            border: 1px solid #000000;
                        }}
                        th {{ font-weight: bold; }}
                    </style>
                </head>
                <body>
                    {html_text}
        </body>
        </html>
            """ 
        
        HTML(string=html_template).write_pdf(file_path,stylesheets=[],optimize_size=("fonts","images"))

    @staticmethod
    def analyze_text(resume_text,job_desc): 
        job_words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#-.]{2,}\b',job_desc)
        common_words = {'the', 'and', 'or', 'as', 'in', 'to', 'you', 'of', 'for', 'with', 'a', 'an', 'is', 'are', 'on', 'your', 'from', 'that', 'this', 'will', 'be', 'have', 'has', 'not', 'at', 'by', 'we', 'us', 'our', 'can', 'should', 'would', 'could', 'their', 'they', 'them', 'it', 'its'}
        job_keywords = [word for word in job_words if word not in common_words]

        resume_lower = resume_text.lower()
        mathes = []
        missing = []

        for keyword in set(job_keywords):
            count = len(re.findall(r'\b' + keyword + r'\b',resume_lower))
            if count > 0:
                mathes.append((keyword,count))
            else:
                keyword_freq = job_desc.lower().count(keyword)
                missing.append((keyword,keyword_freq))
        return {
            "matches": sorted(mathes,key=lambda x: x[1],reverse=True),
            "missing": sorted(missing,key=lambda x: x[1],reverse=True)[:10]
        }

    def _extract_text_from_pdf_sync(self,pdf_path):

        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    async def extract_text_from_pdf(self,pdf_path):
        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._extract_text_from_pdf_sync,
            pdf_path
        )
    
    async def extract_sections(self,text:str):
        sections = {
            "professional_summary": "",
            "skills": "",
            "work_experience": "",
            "education": "",
            "projects": "",
            "certifications": "",
            "other": ""
        }
        
        section_patterns = {
            "professional_summary": r"(?i)(professional\s+summary|summary|profile|about\s+me|career\s+objective)",
            "skills": r"(?i)(skills|technical\s+skills|core\s+competencies|expertise|technologies)",
            "work_experience": r"(?i)(work\s+experience|employment|professional\s+experience|career\s+history)",
            "education": r"(?i)(education|academic|qualifications)",
            "projects": r"(?i)(projects|portfolio)",
            "certifications": r"(?i)(certifications|licenses|courses)",
        }


        lines = text.split("\n")
        current_section = "other"

        for line in lines:
            line = line.strip()

            if not line:
                continue 
            section_found = False
            for section,pattern in section_patterns.items():
                if re.search(pattern,line) and len(line) < 100:
                    current_section = section
                    section_found = True 
                    break
            if not section_found:
                sections[current_section] += line + "\n"
            
        for section in sections:
            sections[section] = sections[section].strip()
            
        return sections

    async def process_resume(self,pdf_file):
        
        resume_text = await self.extract_text_from_pdf(pdf_file) 

        sections = await self.extract_sections(resume_text)

        resume_data = {
        
            "filename" : os.path.basename(pdf_file),
            "full_text" : resume_text,
            **sections            
        }
        return resume_data

    