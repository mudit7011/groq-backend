from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mudit-dev.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use your Groq API key
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.post("/generate-message")
    async def generate_message(data: dict):
    user_type = data.get("userType", "potential client")
    project_context = data.get("projectContext", "web development")
    tone = data.get("tone", "professional")
    subject_idea = data.get("subjectIdea", "")

    system_prompt = f"""
    You are a creative assistant helping users contact Mudit Kumar, a software engineer, for a potential collaboration.

    - Keep the tone {tone}
    - Make it concise, authentic, and personalized
    - Use the provided context if given
    - Start with a subject line like: Subject: ...
    - Follow up with the email body
    - Do NOT say "Here is your message" or any template headers
    """

    if subject_idea:
        user_prompt = (
            f"Write a personalized email from a {user_type} who is interested in building a web app/website for this idea: '{subject_idea}'. "
            "Focus on why they want to collaborate with Mudit, what excites them, and include a subject line at the top."
        )
    else:
        user_prompt = (
            f"Write a personalized email from a {user_type} interested in {project_context}. "
            "Make it friendly and clear, with a subject line and a natural flow."
        )

    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ],
            model="llama3-8b-8192",
        )
        full_message_content = chat_completion.choices[0].message.content

        lines = full_message_content.split('\n', 1)
        subject = lines[0].replace("Subject:", "").strip() if lines else ""
        body = lines[1].strip() if len(lines) > 1 else ""

        return {"subject": subject, "body": body}

    except Exception as e:
        print("❌ Error:", e)
        return {"subject": None, "body": None}

@app.get("/")
async def read_root():
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
