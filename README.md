# Resume Analyzer - RAG System

## Overview

The Resume Analyzer is a Streamlit application that leverages Retrieval-Augmented Generation (RAG) to help you build an ATS-friendly resume. Upload your existing resume in PDF format, provide a job description, and the application will analyze your resume, tailor it to the job description, and generate a new resume optimized for Applicant Tracking Systems (ATS).

## Features

-   **Upload & Analyze Resume**: Upload your resume in PDF format. The application extracts the text and relevant information.
-   **Tailor to Job Description**: Provide a job description, and the application will tailor your resume to match the job requirements.
-   **ATS-Friendly Resume Generation**: Generates a well-structured resume in Markdown format that is optimized for Applicant Tracking Systems.
-   **Edit Resume**: (Future Enhancement) Edit the generated resume to make any necessary changes.
-   **PDF Generation**: (Future Enhancement) Generate a PDF version of the resume for easy sharing.

## Technologies Used

-   **Streamlit**: For creating the user interface.
-   **Langchain**: For language model integration and prompt engineering.
-   **Ollama**: For local language model serving.
-   **Playwright**: For web scraping job descriptions from URLs.
-   **Python**: The primary programming language.
-   **BaseModels**: Custom data models for structured data handling.
-   **PDF Processing**: Utilizes libraries to extract text from PDF files.

## Setup

### Prerequisites

-   Python 3.7+
-   Pip package manager

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Mohit-majumdar/AI-Resume-builder
    cd job-listing-with-llm
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Linux/Mac
    venv\Scripts\activate.bat  # On Windows
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**

    Create a `.env` file in the root directory with the following variables:

    ```
    OPENAI_API_KEY=<your_openai_api_key>
    OLLAMA_BASE_URL=<your_ollama_base_url>
    ```

    Replace `<your_openai_api_key>` with your OpenAI API key and `<your_ollama_base_url>` with the base URL of your Ollama instance.

### Running the Application

```bash
streamlit run app.py
