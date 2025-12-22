from flask import Flask, render_template, request
from groq import Groq
from flask_cors import CORS
from dotenv import load_dotenv
import os
import psycopg
from datetime import datetime
 
app = Flask(__name__)
CORS(app)
 
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
client = Groq(api_key=API_KEY)
 
def get_db_connection():
    """Get database connection"""
    conn = psycopg.connect(DATABASE_URL)
    return conn
 
def save_prompt_response(prompt, response):
    """Save prompt and response to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prompts (prompt, response, timestamp)
        VALUES (%s, %s, %s)
    ''', (prompt, response, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
 
# Initialize database on startup
 
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    prompt = ""
 
    if request.method == "POST":
        prompt = request.form.get("user_prompt", "")
 
        try:
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
            result = f"Error: {e}"
 
        return render_template("result.html", prompt=prompt, result=result)
 
    return render_template("index.html")
 
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)