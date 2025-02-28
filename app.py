import tempfile
import os
import streamlit as st
import asyncio

from tasks import get_job_description, get_altered_summary, create_resume_markdowon
from rag_app import ResumeRag


async def run_async_functions_in_streamlit(function, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await function(*args, **kwargs)


def main():
    st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

    if "rag" not in st.session_state:
        st.session_state.rag = ResumeRag()

    if "resume_data" not in st.session_state:
        st.session_state.resume_data = {}
    
    if "resume_markdown" not in st.session_state:
        st.session_state.resume_markdown = ""

    st.title("📄 Resume Analyzer - RAG System")
    st.markdown(
        """
    This application uses Asynchronous Retrieval-Augmented Generation (RAG) to analyze resumes.
    Upload PDF resumes, search through them, and get insights from the data.
    """
    )

    tab1,tab2,tab3 = st.tabs(["Upload & Analyze Resume","Edit Resume","PDF Genration"])



    with st.sidebar:
        st.header("Navigation")
        st.header("Upload Resumes")

        uploaded_files = st.file_uploader(
            "Choose a file", type="pdf", accept_multiple_files=True
        )

        if uploaded_files:
            upload_button = st.button("Upload files", type="secondary")
            if upload_button:
                progress_bar = st.progress(0)

                async def process_files():
                    for i, file in enumerate(uploaded_files):
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".pdf"
                        ) as temp_file:
                            temp_file.write(file.getvalue())
                            temp_path = temp_file.name

                            result = await st.session_state.rag.process_resume(
                                temp_path
                            )
                            st.session_state.resume_data = result

                            os.unlink(temp_path)
                            progress_bar.progress((i + 1) / len(uploaded_files))
                    return len(uploaded_files)

                async def start_processing():
                    processed_count = await process_files()
                    st.success(f"{processed_count} file processed")
                    st.session_state["file_uploaded"] = True

                asyncio.run(start_processing())
    with tab1:
        if st.session_state.get("file_uploaded", False):
            chat_container = st.container()
            with chat_container:
                with st.chat_message("ai"):
                    st.write("Please enter Job description which you want to apply")

            job_desc = st.chat_input(placeholder="Enter your Job Description")
            if job_desc:
                with chat_container:
                    with st.chat_message("human"):
                        st.write(job_desc)
                        
                async def get_data():
                    with chat_container:
                        with st.spinner("Analyzing job description..."):
                            res_job_desc = await get_job_description(job_desc)
                            st.session_state.job_desc = res_job_desc.get("description", "")
                            st.session_state.skills = res_job_desc.get("skills", [])

                    with chat_container:
                        with st.spinner("Altering Summary for you..."):
                            summary = await get_altered_summary(
                                st.session_state.resume_data.get("professional_summary", ""),
                                st.session_state.job_desc,
                            )
                            st.session_state.resume_data["professional_summary"] = summary.get(
                                "summary", ""
                            )
                            if isinstance(st.session_state.skills, list):
                                st.session_state.resume_data["skills"] = ",".join(
                                    st.session_state.skills
                                )
                            data_dict = st.session_state.resume_data.copy()
                            if "filename" in data_dict:
                                data_dict.pop("filename", None)
                            if "full_text" in data_dict:
                                data_dict.pop("full_text", None)

                        with st.spinner("Building Resume..."):
                            resume_markup = await create_resume_markdowon(data_dict)
                            st.session_state.resume_markdown = resume_markup.get(
                                "resume_markdown", ""
                            )
                    with chat_container:
                        with st.chat_message("ai"):
                            st.write(resume_markup.get("resume_markdown", ""))
                            st.write("🎉 Resume has been generated successfully")
                    
                    if st.session_state.resume_markdown and st.session_state.job_desc:
                        analysis = st.session_state.rag.analyze_text( st.session_state.resume_markdown, st.session_state.job_desc)
                        with chat_container:
                            st.write("### Analysis")
                            st.write(f"Found {len(analysis['matches'])} matching keywords in your resume!")

                            with  st.expander("Show Keywords"):
                                for keyword,count in analysis["matches"]:
                                    st.write(f"- **{keyword}** :  {count} Occurrences")
                            if analysis["missing"]:
                                st.warning("### Consider adding these keywords")
                                for keyword, freq in analysis['missing']:
                                        st.write(f"- **{keyword}** (appears {freq} times in job description)")

                asyncio.run(get_data())

    with tab2:
        if st.session_state.get("resume_markdown", ""):
            st.subheader("Edit Resume")

            edited_resume = st.text_area(
                "Edit your resume", st.session_state.resume_markdown, height=500
            )
            if st.button("Update Resume"):
                st.session_state.resume_markdown = edited_resume
                st.success("Resume updated successfully")

                if st.session_state.resume_markdown and st.session_state.job_desc:
                    analysis = st.session_state.rag.analyze_text(
                        st.session_state.resume_markdown, st.session_state.job_desc
                    )
                    st.write("### Analysis")
                    st.write(f"Found {len(analysis['matches'])} matching keywords in your resume!")

                    with st.expander("Show Keywords"):
                        for keyword, count in analysis["matches"]:
                            st.write(f"- **{keyword}** :  {count} Occurrences")
                    if analysis["missing"]:
                        st.warning("### Consider adding these keywords")
                        for keyword, freq in analysis["missing"]:
                            st.write(f"- **{keyword}** (appears {freq} times in job description)")
        else:
        
            st.info("Please generate a resume in the 'Upload & Analyze' tab first.")

    with tab3:
        if st.session_state.resume_markdown:
            st.subheader("Generate ATS-Friendly PDF")
            st.markdown("### ATS Optimization Tips")
            with st.expander("View ATS Best Practices"):
                st.markdown("""
                - **Use simple formatting** - Avoid tables, columns, headers/footers, images
                - **Standard fonts** - Use Arial, Helvetica, or Times New Roman
                - **Use standard headings** - "Experience," "Education," "Skills"
                - **Avoid abbreviations** - Spell out terms at least once
                - **Include keywords** - Match keywords from the job description
                - **Avoid special characters** - Use standard bullets (• - *)
                - **File format** - PDF is recommended but keep it simple
                """)

            if st.button("Generate ATS-Friendly Resume PDF"):
                try:
                    with tempfile.NamedTemporaryFile(delete=False,suffix="pdf") as temp_file:
                        async def genrate_pdf():
                            with st.spinner("Generating PDF..."):
                                await st.session_state.rag.markdown_to_pdf(
                                    st.session_state.resume_markdown, temp_file.name
                                )
                                with open(temp_file.name, "rb") as file:
                                    pdf = file.read()

                            st.download_button(
                                label="Download ATS-Friendly Resume PDF",
                                data=pdf,
                                file_name="ats_friendly_resume.pdf",
                                mime="application/pdf",
                            )
                        asyncio.run(genrate_pdf())
                        st.success("✅ Resume generated successfully! Click the button above to download your ATS-friendly PDF.")
                        
                        # Clean up the temporary file
                        os.unlink(temp_file.name)
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
                    pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        st.error(f"We are sorry, we are overwhelm with requests. Please try again later. ")
