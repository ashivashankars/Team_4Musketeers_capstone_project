## best backup version 


# import time
# import os
# import json
# import google.generativeai as genai
# import sys

# # --- CONFIGURATION ---
# # REPLACE WITH YOUR API KEY
# os.environ["GOOGLE_API_KEY"] = ""
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# # --- DATA CONFIGURATION ---
# FIELD_CONFIG = {
#     # INTERACTIVE: Critical identity info. If missing, we MUST ask.
#     "graduation_date":      {"id": 1, "text": "Expected Graduation Date", "mode": "interactive"},
#     "current_degree_major": {"id": 2, "text": "Current Degree AND Major (e.g. MS in CS)", "mode": "interactive"},
#     "current_degree_gpa":   {"id": 3, "text": "GPA (For Current Degree Only)", "mode": "interactive"},
    
#     # UPDATED QUESTION 4: Complex Citizenship Logic
#     "us_citizenship":       {"id": 4, "text": "Are you a US Citizen? (If No, specify Visa Type & Sponsorship)", "mode": "interactive"},
    
#     # EXTRACT: Pure extraction.
#     "programming_languages": {"id": 5, "text": "Programming Languages", "mode": "extract"},
#     "experience_software":   {"id": 6, "text": "Work/Project Experience Summary", "mode": "extract"},
#     "tools_frameworks":      {"id": 7, "text": "Tools & Frameworks", "mode": "extract"},
#     "leadership":            {"id": 8, "text": "Leadership Experience", "mode": "extract"},
    
#     # UPDATED QUESTION 9: Replaced Coursework with Job Preference
#     "job_preference":        {"id": 9, "text": "Looking for Full-time / Internship / Both?", "mode": "interactive"},
    
#     "impact_outcomes":       {"id": 10,"text": "Quantifiable Impact & Key Achievements", "mode": "extract"}
# }

# def get_valid_model():
#     print("--- Checking available models... ---")
#     try:
#         available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
#         preferred_order = [
#             "models/gemini-1.5-flash-latest", "models/gemini-1.5-flash",
#             "models/gemini-1.5-pro", "models/gemini-1.5-pro-latest"
#         ]
        
#         for p in preferred_order:
#             if p in available_models:
#                 print(f"Found preferred model: {p}")
#                 return p
        
#         if available_models:
#             return available_models[0]
            
#         raise Exception("No Gemini models found.")
        
#     except Exception as e:
#         print(f"CRITICAL ERROR finding models: {e}")
#         sys.exit(1)

# def wait_for_files_active(files):
#     print("--- Processing Document... ---")
#     for name in (file.name for file in files):
#         file = genai.get_file(name)
#         while file.state.name == "PROCESSING":
#             print(".", end="", flush=True)
#             time.sleep(2)
#             file = genai.get_file(name)
#         if file.state.name != "ACTIVE":
#             raise Exception(f"File {file.name} failed to process")
#     print("\nFile is ready!")

# def main():
#     # 1. SETUP
#     model_name = get_valid_model()
    
#     # 2. GET FILE INPUT
#     print("\n---  INPUT REQUIRED ---")
#     filename = input("Enter the resume filename (e.g., my_cv.pdf): ").strip()
    
#     if not filename:
#         print("No filename provided. Using default 'resume.pdf'...")
#         filename = "resume.pdf"
        
#     if not os.path.exists(filename):
#         print(f" Error: File '{filename}' not found.")
#         return

#     # 3. UPLOAD
#     print(f"--- Uploading {filename} to {model_name} ---")
#     try:
#         pdf_file = genai.upload_file(filename)
#         wait_for_files_active([pdf_file])
#     except Exception as e:
#         print(f"Upload failed: {e}")
#         return

#     # 4. EXTRACTION
#     print("--- Reading Document & Extracting Facts ---")
#     model = genai.GenerativeModel(model_name)
    
#     prompt = f"""
#     You are a precise data extraction agent. 
#     Analyze the attached resume to build a structured candidate profile.

#     Extract the following fields into a JSON object.
    
#     STRICT LOGIC RULES:
#     1. CITIZENSHIP (Q4):
#        - If the resume explicitly states "US Citizen", return "US Citizen".
#        - If it lists a Visa (e.g., F1, H1B, OPT), return "Visa: [Type] (Sponsorship Required/Not Required)".
#        - If NOT stated, return "NULL".
       
#     2. JOB PREFERENCE (Q9):
#        - Check the 'Objective' or 'Summary' section.
#        - Look for keywords like "Seeking Summer 2025 Internship" or "Looking for Full-time roles".
#        - Return "Internship", "Full-time", or "Both".
#        - If not explicitly stated, return "NULL".

#     3. DEGREE & MAJOR (Q2):
#        - Combine Degree Type AND Major (e.g., "Master of Science in Computer Science").
#        - If ambiguous, return "NULL".

#     4. GPA (Q3): 
#        - Extract GPA *only* for the Current/Most Recent degree.
       
#     5. IMPACT (Q10): 
#        - Look for quantifiable metrics (%, $, time saved).
       
#     6. NULL: 
#        - Only use "NULL" if the information is completely absent.
    
#     Required JSON Structure:
#     {{
#         "graduation_date": "value or NULL",
#         "current_degree_major": "value or NULL",
#         "current_degree_gpa": "value or NULL",
#         "us_citizenship": "value or NULL",
#         "programming_languages": "value or NULL",
#         "experience_software": "value or NULL",
#         "tools_frameworks": "value or NULL",
#         "leadership": "value or NULL",
#         "job_preference": "value or NULL",
#         "impact_outcomes": "value or NULL"
#     }}
#     """

#     try:
#         response = model.generate_content(
#             [pdf_file, prompt],
#             generation_config={"response_mime_type": "application/json"}
#         )
#         extracted_data = json.loads(response.text)
#         print("Extraction Successful.\n")
        
#     except Exception as e:
#         print(f"Extraction Error: {e}")
#         extracted_data = {k: "NULL" for k in FIELD_CONFIG.keys()}

#     # 5. HUMAN VERIFICATION
#     print("---  Verifying Data (Human in the Loop) ---")
    
#     null_count = sum(1 for v in extracted_data.values() if v in ["NULL", None, ""])
#     is_blank_resume = null_count >= 8
    
#     if is_blank_resume:
#         print("ALERT: The resume appears to be blank or unreadable.")
#         print("Switching to FULL MANUAL MODE.\n")

#     final_output = {}

#     for key, config in FIELD_CONFIG.items():
#         value = extracted_data.get(key, "NULL")
#         agent_id = config['id']
        
#         is_missing = (value == "NULL" or value is None or value == "")

#         if is_missing:
#             # Interactive Mode OR Blank Resume -> Ask User
#             if config["mode"] == "interactive" or is_blank_resume:
#                 print(f"[MISSING] Agent {agent_id}: {config['text']}?")
#                 user_input = input(f"   >>> Input: ")
#                 final_output[key] = user_input
#             else:
#                 final_output[key] = "Not Found in Resume"
#         else:
#             final_output[key] = value

#     # 6. OUTPUT
#     print("\n---  Final Candidate Profile ---")
#     print(json.dumps(final_output, indent=4))
    
#     with open("candidate_profile.json", "w") as f:
#         json.dump(final_output, f, indent=4)
#     print("\nSaved to candidate_profile.json")

# if __name__ == "__main__":
#     main()


import time
import os
import json
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURATION ---
# 1. Load environment variables
load_dotenv()

# 2. Get Key securely
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file.")
    print("Please create a .env file with: GOOGLE_API_KEY=your_key_here")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# --- DATA CONFIGURATION ---
FIELD_CONFIG = {
    # INTERACTIVE
    "graduation_date":      {"id": 1, "text": "Expected Graduation Date", "mode": "interactive"},
    "current_degree_major": {"id": 2, "text": "Current Degree AND Major (e.g. MS in CS)", "mode": "interactive"},
    "current_degree_gpa":   {"id": 3, "text": "GPA (For Current Degree Only)", "mode": "interactive"},
    "us_citizenship":       {"id": 4, "text": "Are you a US Citizen? (If No, specify Visa Type & Sponsorship)", "mode": "interactive"},
    
    # EXTRACT
    "programming_languages": {"id": 5, "text": "Programming Languages", "mode": "extract"},
    "experience_software":   {"id": 6, "text": "Work/Project Experience Summary", "mode": "extract"},
    "tools_frameworks":      {"id": 7, "text": "Tools & Frameworks", "mode": "extract"},
    
    # Q8: LEADERSHIP (Now Key-Value Structured)
    "leadership":            {"id": 8, "text": "Leadership Experience", "mode": "extract"},
    
    "job_preference":        {"id": 9, "text": "Looking for Full-time / Internship / Both?", "mode": "interactive"},
    "impact_outcomes":       {"id": 10,"text": "Quantifiable Impact & Key Achievements", "mode": "extract"}
}

def get_valid_model():
    print("--- Checking available models... ---")
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        preferred_order = [
            "models/gemini-1.5-flash-latest", "models/gemini-1.5-flash",
            "models/gemini-1.5-pro", "models/gemini-1.5-pro-latest"
        ]
        
        for p in preferred_order:
            if p in available_models:
                print(f"Found preferred model: {p}")
                return p
        
        if available_models:
            return available_models[0]
            
        raise Exception("No Gemini models found.")
        
    except Exception as e:
        print(f"CRITICAL ERROR finding models: {e}")
        sys.exit(1)

def wait_for_files_active(files):
    print("--- Processing Document... ---")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("\nFile is ready!")

def main():
    # 1. SETUP
    model_name = get_valid_model()
    
    # 2. GET FILE INPUT
    print("\n--- INPUT REQUIRED ---")
    filename = input("Enter the resume filename (e.g., my_cv.pdf): ").strip()
    
    if not filename:
        print("No filename provided. Using default 'resume.pdf'...")
        filename = "resume.pdf"
        
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    # 3. UPLOAD
    print(f"--- Uploading {filename} to {model_name} ---")
    try:
        pdf_file = genai.upload_file(filename)
        wait_for_files_active([pdf_file])
    except Exception as e:
        print(f"Upload failed: {e}")
        return

    # 4. EXTRACTION
    print("--- Reading Document & Extracting Facts ---")
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are a precise data extraction agent. 
    Analyze the attached resume to build a structured candidate profile.

    Extract the following fields into a JSON object.
    
    STRICT LOGIC RULES:
    1. LEADERSHIP (Q8):
       - Extract leadership roles into a LIST of OBJECTS.
       - Each object must have: "role" (e.g. President, Lead), "organization" (e.g. ACM Club), and "description" (brief summary).
       - If no leadership is found, return "NULL".
       
    2. CITIZENSHIP (Q4):
       - If "US Citizen" -> "US Citizen".
       - If Visa -> "Visa: [Type] (Sponsorship Required/Not Required)".
       - Else -> "NULL".

    3. JOB PREFERENCE (Q9):
       - Look for "Seeking Internship/Full-time" in Summary/Objective.
       - Return "Internship", "Full-time", or "Both".
       - Else -> "NULL".

    4. DEGREE & GPA: 
       - Combine Degree + Major (e.g. "MS in CS").
       - GPA only for current degree.
       
    5. NULL: 
       - Only use "NULL" (string) if completely absent.
    
    Required JSON Structure:
    {{
        "graduation_date": "value or NULL",
        "current_degree_major": "value or NULL",
        "current_degree_gpa": "value or NULL",
        "us_citizenship": "value or NULL",
        "programming_languages": "value or NULL",
        "experience_software": "value or NULL",
        "tools_frameworks": "value or NULL",
        "leadership": [
            {{ "role": "...", "organization": "...", "description": "..." }},
            {{ "role": "...", "organization": "...", "description": "..." }}
        ] or "NULL",
        "job_preference": "value or NULL",
        "impact_outcomes": "value or NULL"
    }}
    """

    try:
        response = model.generate_content(
            [pdf_file, prompt],
            generation_config={"response_mime_type": "application/json"}
        )
        extracted_data = json.loads(response.text)
        print("Extraction Successful.\n")
        
    except Exception as e:
        print(f" Extraction Error: {e}")
        extracted_data = {k: "NULL" for k in FIELD_CONFIG.keys()}

    # 5. HUMAN VERIFICATION
    print("--- Verifying Data (Human in the Loop) ---")
    
    null_count = sum(1 for v in extracted_data.values() if v in ["NULL", None, ""])
    is_blank_resume = null_count >= 8
    
    if is_blank_resume:
        print("ALERT: The resume appears to be blank or unreadable.")
        print("Switching to FULL MANUAL MODE.\n")

    final_output = {}

    for key, config in FIELD_CONFIG.items():
        value = extracted_data.get(key, "NULL")
        agent_id = config['id']
        
        is_missing = (value == "NULL" or value is None or value == "")

        if is_missing:
            if config["mode"] == "interactive" or is_blank_resume:
                print(f"[MISSING] Agent {agent_id}: {config['text']}?")
                user_input = input(f"   >>> Input: ")
                final_output[key] = user_input
            else:
                final_output[key] = "Not Found in Resume"
        else:
            final_output[key] = value

    # 6. OUTPUT
    print("\n--- Final Candidate Profile ---")
    print(json.dumps(final_output, indent=4))
    
    with open("candidate_profile.json", "w") as f:
        json.dump(final_output, f, indent=4)
    print("\nSaved to candidate_profile.json")

if __name__ == "__main__":
    main()