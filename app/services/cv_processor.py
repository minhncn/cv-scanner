import fitz  # PyMuPDF
import os
import json
import requests
import google.generativeai as gen_ai

def extract_text_from_pdf(file):
    pdf_document = fitz.open(stream=file.file.read(), filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text("text") or ""
    pdf_document.close()
    # Save raw text to a file for record-keeping
    with open("services/raw_cv_texts.txt", "a", encoding="utf-8") as f:
        f.write("----- NEW CV -----\n")
        f.write(text)
        f.write("\n\n")
    return text

def process_cv_to_json(raw_text):
    gen_ai.config(api_key = os.getenv("GEMINI_API_KEY")) 
    model = gen_ai.Model("gemini-1.5-flash") 
    prompt = f"""
    Convert the following CV text into a structured JSON format with these fields:
    - name: string
    - email: string
    - phone: string
    - education: string
    - skills: list of strings
    - work_experience: list of objects with company, position, start_date, end_date, description
    
    CV Text:
    {raw_text}
    
    Return only the JSON object.
    """
    response = model.generate_content(prompt)
    result = response.json()["response"]
    try:
        return json.loads(response.text.strip())
    except:
        raise ValueError("Failed to parse CV content")
    
def process_cv_to_json_ollama(raw_text):
    prompt = f"""
    Convert the following CV text into a structured JSON format with these fields:
    - name: string
    - email: string
    - phone: string
    - education: string
    - skills: list of strings
    - work_experience: list of objects with company, position, start_date, end_date, description
    
    CV Text:
    {raw_text}
    
    Return only the JSON object.
    """
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )
    result = response.json()["response"]
    try: 
        return json.loads(result.strip())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse CV content. Response: " + result)