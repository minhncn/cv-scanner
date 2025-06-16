from fastapi import HTTPException
import requests
import json
import re

def process_cv_with_ollama(raw_text):
    prompt = f"""
    Convert the following CV text into a structured JSON format with these fields:
    - name: string
    - email: string
    - phone: string
    - education: object with school, degree, major_gpa, courses (list)
    - skills: list of strings
    - work_experience: list of objects with company, position, start_date, end_date, description
    
    CV Text:
    {raw_text}
    
    Return only the JSON object wrapped in ```json\n...\n```.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json().get("response", "")
        print("Ollama raw result:", result)  # Debug
        
        # Extract JSON from ```json\n...\n```
        json_match = re.search(r'```json\n(.*?)\n```', result, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            parsed_data = json.loads(json_str)
            
            # Serialize education to JSON string for Text column
            if isinstance(parsed_data.get("education"), dict):
                parsed_data["education"] = json.dumps(parsed_data["education"])
            
            # Serialize skills to comma-separated string or JSON string
            if isinstance(parsed_data.get("skills"), list):
                parsed_data["skills"] = ",".join(parsed_data["skills"])  # E.g., "Java,SQL"
                # Alternatively: parsed_data["skills"] = json.dumps(parsed_data["skills"])
            
            print("Parsed CV:", json.dumps(parsed_data, indent=2, ensure_ascii=False))
            return parsed_data  # Return the parsed CV directly
        else:
            raise ValueError(f"No JSON object found in Ollama response. Raw response: {result}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 405:
            raise HTTPException(status_code=405, detail="Ollama endpoint /api/generate not supported. Check server or try /api/chat.")
        raise HTTPException(status_code=500, detail=f"Ollama HTTP error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {e}")