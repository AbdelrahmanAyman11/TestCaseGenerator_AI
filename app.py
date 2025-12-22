from flask import Flask, render_template, request
from groq import Groq
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

# Try to import psycopg2, but make it optional
try:
    import psycopg2
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False
    print("WARNING: psycopg2 not available. Database features will be disabled.")
 
app = Flask(__name__)
CORS(app)
 
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=API_KEY)
 
def get_db_connection():
    """Get database connection"""
    if not PSYCOPG_AVAILABLE or not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def save_prompt_response(prompt, response):
    """Save prompt and response to database"""
    if not PSYCOPG_AVAILABLE:
        print("Database not available - skipping save")
        return
    
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL is not set. Data will not be saved to database.")
        return
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prompts (prompt, response, timestamp)
                VALUES (%s, %s, %s)
            ''', (prompt, response, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            print("Data saved successfully to database")
        else:
            print("ERROR: Failed to establish database connection")
    except Exception as e:
        print(f"Database error: {e}")  # Log error but don't crash
 
# Initialize database on startup
 
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    prompt = ""
 
    if request.method == "POST":
        prompt = request.form.get("user_prompt", "")
 
        try:
            if not prompt.strip():
                result = "Error: Please enter a prompt"
            else:
                completion = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=1,
                    max_tokens=1024,
                    top_p=1
                )
                result = completion.choices[0].message.content
               
                # Save prompt and response to database
                save_prompt_response(prompt, result)
 
        except Exception as e:
            result = f"Error: {str(e)}"
 
        return render_template("result.html", prompt=prompt, result=result)
 
    return render_template("index.html")
 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)