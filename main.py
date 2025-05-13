import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
import os
import requests
from bs4 import BeautifulSoup
import subprocess
import sys
import json
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def parse_resume(resume_text):
    """Parse resume text to extract key information."""
    # This is a simple parser - would need to be improved with regex or NLP
    resume_data = {
        "full_name": "",
        "email": "",
        "phone": "",
        "education": [],
        "experience": [],
        "skills": []
    }
    
    lines = resume_text.split('\n')
    
    # Very basic parsing logic - this should be enhanced with better algorithms
    for i, line in enumerate(lines):
        # Find name (assume it's one of the first few lines)
        if i < 5 and not resume_data["full_name"] and len(line.strip()) > 0:
            resume_data["full_name"] = line.strip()
        
        # Look for email
        if '@' in line and '.' in line and not resume_data["email"]:
            words = line.split()
            for word in words:
                if '@' in word and '.' in word:
                    resume_data["email"] = word.strip()
        
        # Look for phone (simple pattern)
        if any(c.isdigit() for c in line) and not resume_data["phone"]:
            # Extract sequences of digits and common separators
            for word in line.split():
                if sum(c.isdigit() for c in word) >= 7:  # Most phone numbers have at least 7 digits
                    resume_data["phone"] = word.strip()
        
        # Identify sections (crude approach)
        if "EDUCATION" in line.upper() or "ACADEMIC" in line.upper():
            section = "education"
            continue
        elif "EXPERIENCE" in line.upper() or "EMPLOYMENT" in line.upper() or "WORK" in line.upper():
            section = "experience"
            continue
        elif "SKILLS" in line.upper() or "PROFICIENCIES" in line.upper() or "TECHNOLOGIES" in line.upper():
            section = "skills"
            continue
            
        # Add content to current section
        if 'section' in locals():
            if section == "education" and line.strip():
                resume_data["education"].append(line.strip())
            elif section == "experience" and line.strip():
                resume_data["experience"].append(line.strip())
            elif section == "skills" and line.strip():
                resume_data["skills"].append(line.strip())
    
    return resume_data

def generate_prompt(resume_data, job_link):
    """Generate a prompt for browser automation based on resume data and job link."""
    
    # Get job details if link is provided
    job_title = "the position"
    company = "the company"
    
    if job_link:
        try:
            response = requests.get(job_link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Try to extract job title and company (basic approach)
                title_tags = soup.find_all(['h1', 'h2'], class_=['job-title', 'jobtitle', 'job_title'])
                if title_tags:
                    job_title = title_tags[0].get_text().strip()
                
                company_tags = soup.find_all(['span', 'div', 'a'], class_=['company', 'company-name'])
                if company_tags:
                    company = company_tags[0].get_text().strip()
        except:
            pass
    
    # Format education, experience, and skills for readability
    education = "\n     - " + "\n     - ".join(resume_data["education"][:3]) if resume_data["education"] else "N/A"
    experience = "\n     - " + "\n     - ".join(resume_data["experience"][:3]) if resume_data["experience"] else "N/A"
    skills = "\n     - " + "\n     - ".join(resume_data["skills"][:5]) if resume_data["skills"] else "N/A"
    
    prompt = f"""
Instruction:
You are filling out an online job application for {job_title} at {company}. Populate every field exactly as specified from the candidate's resume without altering or omitting details.

Resume Details:

- Full Name: {resume_data["full_name"]}
- Email: {resume_data["email"]}
- Phone: {resume_data["phone"]}

- Education:{education}

- Experience:{experience}

- Skills:{skills}

Action Steps:
1. Open the job application form at {job_link}
2. Look for the "Apply" or "Apply Now" button and click it
3. For each form field, fill in the matching information from the resume details above
4. If asked for a cover letter, write one that highlights how the candidate's experience matches the job requirements
5. Review the completed form to ensure all fields are filled correctly
6. Submit the application when everything is complete

End Condition:
After clicking the submit button and confirming the application is submitted, say "Application successfully submitted for {job_title} at {company}. Task complete." and end the session.

Thank you.
"""
    return prompt

def modify_agent_py(prompt):
    """Modify the agent.py file to use the new prompt."""
    try:
        # Path to the agent.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agent_path = os.path.join(script_dir, "browser-use", "agent.py")
        
        # Check if agent.py exists
        if not os.path.exists(agent_path):
            messagebox.showerror("Error", f"Could not find agent.py at {agent_path}")
            return False
            
        # Read the current agent.py content
        with open(agent_path, 'r') as f:
            content = f.read()
            
        # Replace the task section using regex
        task_pattern = r'task="""(.*?)""",'
        if re.search(task_pattern, content, re.DOTALL):
            new_content = re.sub(task_pattern, f'task="""{prompt}""",', content, flags=re.DOTALL)
            
            # Write the modified content back
            with open(agent_path, 'w') as f:
                f.write(new_content)
                
            return True
        else:
            messagebox.showerror("Error", "Could not find the task section in agent.py")
            return False
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to modify agent.py: {str(e)}")
        return False

def run_browser_agent():
    """Run the browser-use agent script."""
    try:
        # Path to the agent.py script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        agent_path = os.path.join(script_dir, "browser-use", "agent.py")
        
        # Run the agent
        process = subprocess.Popen(
            [sys.executable, agent_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        messagebox.showinfo("Agent Started", "Browser automation agent has been launched.")
        return True
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start browser agent: {str(e)}")
        return False

def upload_file():
    file_path = filedialog.askopenfilename(title="Upload Resume", filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx"), ("All files", "*.*")])
    if file_path:
        file_label.config(text=f"Selected: {file_path}")
        global resume_path
        resume_path = file_path

def submit_link():
    link = link_entry.get()
    link_label.config(text=f"Submitted Link: {link}")
    
    # Check if resume was uploaded
    if 'resume_path' in globals() and os.path.exists(resume_path):
        # Process the resume and generate a prompt
        if resume_path.lower().endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_path)
            resume_data = parse_resume(resume_text)
            prompt = generate_prompt(resume_data, link)
            
            # Display prompt in a new window
            prompt_window = tk.Toplevel(root)
            prompt_window.title("Generated Prompt")
            prompt_window.geometry("800x600")
            
            prompt_text = tk.Text(prompt_window, wrap=tk.WORD)
            prompt_text.insert(tk.END, prompt)
            prompt_text.pack(fill=tk.BOTH, expand=True)
            
            # Add buttons
            button_frame = tk.Frame(prompt_window)
            button_frame.pack(pady=10)
            
            def copy_to_clipboard():
                prompt_window.clipboard_clear()
                prompt_window.clipboard_append(prompt_text.get("1.0", tk.END))
                copy_button.config(text="Copied!")
                prompt_window.after(1000, lambda: copy_button.config(text="Copy to Clipboard"))
                
            copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard)
            copy_button.pack(side=tk.LEFT, padx=10)
            
            # Add button to update agent.py and run it
            def update_and_run_agent():
                if modify_agent_py(prompt_text.get("1.0", tk.END)):
                    run_browser_agent()
            
            run_agent_button = tk.Button(
                button_frame, 
                text="Update & Launch Browser Agent", 
                command=update_and_run_agent
            )
            run_agent_button.pack(side=tk.LEFT, padx=10)
            
        else:
            link_label.config(text="Only PDF resumes are supported currently")
    else:
        link_label.config(text="Please upload a resume first")

# Create the main window
root = tk.Tk()
root.title("Seamless Job Application Copilot")
root.geometry("500x300")

# Resume path global variable
resume_path = None

# Upload button
upload_button = tk.Button(root, text="Upload Resume", command=upload_file)
upload_button.pack(pady=10)

# Display selected file
file_label = tk.Label(root, text="No file selected")
file_label.pack()

# Job link entry
tk.Label(root, text="Enter Job Posting URL:").pack(pady=(20, 5))
link_entry = tk.Entry(root, width=50)
link_entry.pack()

submit_button = tk.Button(root, text="Generate Job Application Prompt", command=submit_link)
submit_button.pack(pady=20)

# Display submitted link status
link_label = tk.Label(root, text="")
link_label.pack()

root.mainloop()
