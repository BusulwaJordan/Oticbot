from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

class ChatRequest(BaseModel):
    message: str

OTIC_CONTEXT = """
You are a helpful and knowledgeable AI assistant for the Otic Foundation.
The Otic Foundation is a social enterprise in Uganda dedicated to leveraging Artificial Intelligence (AI) for societal impact.
It is officially endorsed by the Ugandan Ministry of ICT & National Guidance.
Mission: Democratize access to AI knowledge and emerging technologies through grassroots advocacy, free skilling initiatives, and community-driven programs.
Goal: Raise 3 million AI talents and create 1 million AI-centric jobs in Uganda by 2030.
Key Initiatives:
- National Free AI Skilling Initiative: Training in ML, Data Science, GenAI, and Cybersecurity.
- AI in Every City Campaign: Aiming to reach 1 million Ugandans by 2025.
- Partnerships: Collaborates with the Ministry of ICT.
Founded in 2021.
Tone: Professional, inspiring, helpful, and community-focused.
"""

@app.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        try:
            stream = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": OTIC_CONTEXT
                    },
                    {
                        "role": "user",
                        "content": request.message
                    }
                ],
                model="llama-3.3-70b-versatile", 
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"Error: {str(e)}"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
