# ========================================
# app.py - Complete Flask App (Corrected)
# ========================================

from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import time
import google.generativeai as genai

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

# ============================================
# CREATE FLASK APP
# ============================================

app = Flask(__name__)

# ============================================
# GEMINI AI SETUP (CORRECTED)
# ============================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Create model
model = genai.GenerativeModel("gemini-1.5-flash")

# ============================================
# FUNCTION 1: Validate User Input
# ============================================

def validate_career_input(career):
    """
    Validates the career input from user.
    Returns (is_valid, error_message)
    """

    # Check if empty
    if not career:
        return False, "⚠️ Please enter a career goal!"

    # Check minimum length
    if len(career) < 3:
        return False, "⚠️ Career name is too short! Please be more specific."

    # Check maximum length
    if len(career) > 100:
        return False, "⚠️ Career name is too long! Keep it under 100 characters."

    # Check for numbers only
    if career.isdigit():
        return False, "⚠️ Please enter a valid career name!"

    # All checks passed
    return True, None


# ============================================
# FUNCTION 2: Build Prompt
# ============================================

def build_prompt(career):

    prompt = f"""
Career: {career}

Give me exactly in this format:

## 🗺️ LEARNING ROADMAP
- Phase 1 (Beginner): what to learn
- Phase 2 (Intermediate): what to learn
- Phase 3 (Advanced): what to learn

## 💡 REQUIRED SKILLS
- Skill 1
- Skill 2
- Skill 3
- Skill 4
- Skill 5

## 🛠️ TOOLS TO LEARN
- Tool 1
- Tool 2
- Tool 3
- Tool 4
- Tool 5

## 🚀 PROJECT IDEAS
- Project 1
- Project 2
- Project 3
- Project 4

## ⏱️ LEARNING TIMELINE
- Month 1-3: Beginner
- Month 4-6: Intermediate
- Month 7-12: Job Ready

## 💰 SALARY OUTLOOK
- Entry: range
- Mid: range
- Senior: range

Keep it short.
Bullet points only.
"""

    return prompt


# ============================================
# FUNCTION 3: Parse Roadmap Into Sections
# ============================================

def parse_roadmap(roadmap_text):

    sections = {
        'roadmap': '',
        'skills': '',
        'tools': '',
        'projects': '',
        'timeline': '',
        'salary': ''
    }

    section_map = {
        'ROADMAP': 'roadmap',
        'SKILLS': 'skills',
        'TOOLS': 'tools',
        'PROJECT': 'projects',
        'TIMELINE': 'timeline',
        'SALARY': 'salary'
    }

    current_section = None

    lines = roadmap_text.split('\n')

    for line in lines:

        if line.startswith('##'):

            current_section = None
            line_upper = line.upper()

            for keyword, section_key in section_map.items():

                if keyword in line_upper:
                    current_section = section_key
                    break

        elif current_section:

            cleaned_line = line.strip()

            if cleaned_line:
                sections[current_section] += cleaned_line + '\n'

    # Remove extra spaces
    for key in sections:
        sections[key] = sections[key].strip()

    return sections


# ============================================
# FUNCTION 4: Fallback Roadmap
# ============================================

def get_fallback_roadmap(career):

    return f"""
## 🗺️ LEARNING ROADMAP
- Phase 1 (Beginner): Learn fundamentals of {career}
- Phase 2 (Intermediate): Build projects and practice
- Phase 3 (Advanced): Apply for jobs and specialize

## 💡 REQUIRED SKILLS
- Problem Solving
- Communication
- Git & GitHub
- Teamwork
- Continuous Learning

## 🛠️ TOOLS TO LEARN
- VS Code
- Git
- GitHub
- Linux
- Docker

## 🚀 PROJECT IDEAS
- Beginner Project
- Portfolio Website
- Real-world App
- Final Capstone Project

## ⏱️ LEARNING TIMELINE
- Month 1-3: Basics
- Month 4-6: Intermediate
- Month 7-12: Job Ready

## 💰 SALARY OUTLOOK
- Entry: 3-6 LPA
- Mid: 8-15 LPA
- Senior: 20+ LPA
"""


# ============================================
# FUNCTION 5: Generate Roadmap
# ============================================

def generate_roadmap(career):

    try:

        # Small delay
        time.sleep(1)

        # Build prompt
        prompt = build_prompt(career)

        # Generate response from Gemini
        response = model.generate_content(prompt)

        print("✅ Gemini AI responded!")

        return response.text

    except Exception as e:

        print(f"⚠️ API Error - Using fallback: {str(e)}")

        return get_fallback_roadmap(career)


# ============================================
# ROUTE 1: Homepage
# ============================================

@app.route('/', methods=['GET'])
def home():

    return render_template('index.html')


# ============================================
# ROUTE 2: Generate Roadmap
# ============================================

@app.route('/generate', methods=['POST'])
def generate():

    # Read input
    career = request.form.get('career', '').strip()

    # Validate input
    is_valid, error_message = validate_career_input(career)

    # If invalid
    if not is_valid:

        return render_template(
            'index.html',
            error=error_message
        )

    # Console log
    print(f"\n{'='*50}")
    print(f"🎯 Generating roadmap for: {career}")
    print(f"{'='*50}\n")

    # Generate roadmap
    roadmap_text = generate_roadmap(career)

    # Parse sections
    roadmap_sections = parse_roadmap(roadmap_text)

    print("✅ Sections parsed!")

    # Send to result page
    return render_template(
        'result.html',
        career=career,
        roadmap_sections=roadmap_sections
    )


# ============================================
# ERROR HANDLER: 404
# ============================================

@app.errorhandler(404)
def page_not_found(error):

    print(f"❌ 404 Error: {error}")

    return render_template('404.html'), 404


# ============================================
# ERROR HANDLER: 500
# ============================================

@app.errorhandler(500)
def server_error(error):

    print(f"❌ 500 Error: {error}")

    return render_template('500.html'), 500


# ============================================
# RUN FLASK APP
# ============================================

if __name__ == '__main__':
    app.run(debug=True)
