import streamlit as st
import PyPDF2
from mistralai.client import MistralClient
import edge_tts
import asyncio
import tempfile

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def summarize_text(text, api_key):
    try:
        client = MistralClient(api_key=api_key)
        response = client.chat(
            model="mistral-7b-instruct",
            messages=[{"role": "user", "content": f"Summarize this text:\n{text}"}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"

def generate_audio(text, output_file):
    try:
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        asyncio.run(communicate.save(output_file))
        return output_file
    except Exception as e:
        return None

def main():
    st.set_page_config(page_title="PDF Summarizer", page_icon="📄", layout="wide")
    st.title("PDF Summarizer with TTS")

    st.sidebar.title("Upload PDF & API Key")
    user_api_key = st.sidebar.text_input("Enter Open-Source LLM API Key", type="password")
    uploaded_pdf = st.sidebar.file_uploader("Upload a PDF", type="pdf")

    if uploaded_pdf and user_api_key:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_pdf.getvalue())
            pdf_path = tmp_file.name
        
        st.subheader("Extracting text...")
        extracted_text = extract_text_from_pdf(pdf_path)
        st.text_area("Extracted Text", extracted_text[:1000] + "...", height=200)
        
        st.subheader("Summarizing...")
        summary = summarize_text(extracted_text, user_api_key)
        st.write(summary)
        
        st.subheader("Generating Audio...")
        audio_path = generate_audio(summary, "summary.mp3")
        if audio_path:
            st.audio(audio_path, format="audio/mp3")
        else:
            st.error("Failed to generate audio.")

if __name__ == "__main__":
    main()
