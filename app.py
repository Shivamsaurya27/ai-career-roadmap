# ============================================
# app.py - Complete Flask App with Error Handling
# ============================================

from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import time
from google import genai

# Load .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Setup Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================
# FUNCTION 1: Validate User Input
# Checks if career input is valid
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
    # A career name should be at least 3 characters
    if len(career) < 3:
        return False, "⚠️ Career name is too short! Please be more specific."

    # Check maximum length
    # Prevent very long inputs that waste API quota
    if len(career) > 100:
        return False, "⚠️ Career name is too long! Keep it under 100 characters."

    # Check for numbers only
    # "123" is not a valid career
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
    - Skill 1, Skill 2, Skill 3, Skill 4, Skill 5

    ## 🛠️ TOOLS TO LEARN
    - Tool 1, Tool 2, Tool 3, Tool 4, Tool 5

    ## 🚀 PROJECT IDEAS
    - Project 1, Project 2, Project 3, Project 4

    ## ⏱️ LEARNING TIMELINE
    - Month 1-3: Beginner
    - Month 4-6: Intermediate
    - Month 7-12: Job Ready

    ## 💰 SALARY OUTLOOK
    - Entry: range
    - Mid: range
    - Senior: range

    Keep it short. Bullet points only.
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

    for key in sections:
        sections[key] = sections[key].strip()

    return sections


# ============================================
# FUNCTION 4: Fallback Roadmap
# ============================================
def get_fallback_roadmap(career):
    return f"""## 🗺️ LEARNING ROADMAP
- Phase 1 (Beginner): Learn fundamentals of {career}, take online courses, practice daily
- Phase 2 (Intermediate): Build real projects, learn industry tools, join communities
- Phase 3 (Advanced): Specialize in a niche, contribute to open source, apply for jobs

## 💡 REQUIRED SKILLS
- Programming fundamentals
- Problem solving and logic
- Version control with Git
- Communication and teamwork
- Continuous learning mindset

## 🛠️ TOOLS TO LEARN
- VS Code (Code Editor)
- Git and GitHub (Version Control)
- Linux Terminal (Command Line)
- Docker (Containerization)
- Relevant {career} frameworks

## 🚀 PROJECT IDEAS
- Project 1: Build a beginner level {career} project
- Project 2: Clone a popular app in your field
- Project 3: Build something that solves a real problem
- Project 4: Create a capstone project for portfolio

## ⏱️ LEARNING TIMELINE
- Month 1-3: Learn basics and complete online courses
- Month 4-6: Build portfolio projects and network
- Month 7-9: Apply for internships or junior roles
- Month 10-12: Interview preparation and job applications

## 💰 SALARY OUTLOOK
- Entry Level: 3-6 LPA India / 60-80k USD
- Mid Level: 8-15 LPA India / 90-120k USD
- Senior Level: 20-40 LPA India / 140-180k USD"""


# ============================================
# FUNCTION 5: Generate Roadmap
# ============================================
def generate_roadmap(career):
    try:
        time.sleep(1)
        prompt = build_prompt(career)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
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

    # Read and clean career input
    career = request.form.get('career', '').strip()

    # Validate input
    is_valid, error_message = validate_career_input(career)

    # If invalid, send back to homepage with error
    if not is_valid:
        return render_template(
            'index.html',
            error=error_message
        )

    # Log to terminal
    print(f"\n{'='*50}")
    print(f"🎯 Generating roadmap for: {career}")
    print(f"{'='*50}\n")

    # Generate roadmap
    roadmap_text = generate_roadmap(career)

    # Parse into sections
    roadmap_sections = parse_roadmap(roadmap_text)

    print("✅ Sections parsed!")

    # Send to result page
    return render_template(
        'result.html',
        career=career,
        roadmap_sections=roadmap_sections
    )


# ============================================
# ERROR HANDLER: 404 Not Found
# Shows when user visits wrong URL
# ============================================
@app.errorhandler(404)
def page_not_found(error):
    """
    This function runs when user visits
    a URL that doesn't exist.
    Example: localhost:5000/xyz
    """
    print(f"❌ 404 Error: {error}")
    return render_template('404.html'), 404


# ============================================
# ERROR HANDLER: 500 Server Error
# Shows when something crashes in our code
# ============================================
@app.errorhandler(500)
def server_error(error):
    """
    This function runs when our code crashes.
    Instead of showing ugly Flask error page,
    we show a nice friendly error page.
    """
    print(f"❌ 500 Error: {error}")
    return render_template('500.html'), 500


# ============================================
# RUN THE APP
# ============================================
if __name__ == '__main__':
    app.run(debug=True)