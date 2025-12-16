from flask import Flask, render_template, request
from groq import Groq
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

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

        except Exception as e:
            result = f"Error: {e}"

        return render_template("result.html", prompt=prompt, result=result)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
