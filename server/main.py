from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import re
import time
from collections import defaultdict
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

# ============================================
# GUARDRAILS CONFIGURATION
# ============================================

# Rate Limiting: Track requests per IP
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # Max requests per window
RATE_LIMIT_WINDOW = 60    # Time window in seconds (1 minute)

# Maximum response length (characters)
MAX_RESPONSE_LENGTH = 1500

# Blocked keywords/phrases (case-insensitive)
BLOCKED_KEYWORDS = [
    # Harmful content
    "how to hack", "hack into", "bypass security", "steal password",
    "make a bomb", "create virus", "malware", "ransomware",
    # Inappropriate requests
    "write my essay", "do my homework", "complete my assignment",
    "generate code for", "write code", "python script", "javascript code",
    # Jailbreak attempts
    "ignore your instructions", "forget your rules", "pretend you are",
    "act as if", "roleplay as", "you are now", "new persona",
    "ignore previous", "disregard your", "bypass your",
    # Sensitive topics
    "political opinion", "who to vote", "religious belief",
]

# Response for blocked content
BLOCKED_RESPONSE = """I'm sorry, but I can't help with that request. 

I'm OticBot, specifically designed to assist with questions about the Otic Foundation and our AI education initiatives in Uganda. 

Is there anything about our programs, how to get involved, or AI education that I can help you with?"""

# Response for rate limiting
RATE_LIMIT_RESPONSE = """You're sending messages too quickly! Please wait a moment before trying again.

In the meantime, feel free to explore the Otic Foundation's mission of democratizing AI education in Uganda. 🇺🇬"""

OTIC_CONTEXT = """
You are OticBot, the official AI assistant for the Otic Foundation.

=== 1. OTIC FOUNDATION (PARENT ORGANIZATION) ===
- **Website**: https://oticfoundation.org
- **Mission**: Democratize access to AI knowledge and emerging technologies through grassroots advocacy, free skilling initiatives, and community-driven programs.
- **Vision**: An inclusive, AI-empowered society where every community in Uganda and Africa can thrive in the digital age.
- **Core Values**: Innovation, Collaboration, Impact, Ethical Integrity.
- **Goals**: Raise 3 million AI talents & create 1 million AI-centric jobs in Uganda by 2030.
- **Location**: National ICT Innovation Hub, Nakawa, Kampala, Uganda.
- **Contact**: +256 756722263 / +256 706867547 | info@oticfoundation.org

=== 2. OTIC ACADEMY (YOUTH SKILLING) ===
- **Website**: https://academy.oticfoundation.org
- **Focus**: Equipping young minds/students with hands-on tech skills.
- **Key Offerings**:
  1. **Learn Data Analytics**:
     - *Curriculum*: Python, SQL, R, NumPy, Pandas, Data Science basics.
     - *Goal*: Analyze, visualize, and interpret data to solve real-world problems.
  2. **Vacists AI Program**:
     - *Target*: S4 & S6 vacists.
     - *Content*: Python, R, SQL with W3Schools certification.
  3. **Cybersecurity** (Coming Soon):
     - *Goal*: Transform beginners into experts to protect against modern threats.
- **Why Otic Academy?**:
  - Global Recognition (Otic + W3Schools certs).
  - Flexible online learning.
  - Career-focused curriculum.

=== 3. OTIC INSTITUTE OF EMERGING TECHNOLOGIES (OIET - PROFESSIONAL) ===
- **Website**: https://oiet.ac.ug
- **Focus**: Specialized AI certifications for professionals (Finance, Insurance, Tax, Marketing, Risk).
- **Certifications**:
  1. **Smart Insurance** (AI for Underwriting & Retention):
     - *Problem*: High churn, generic products, slow underwriting.
     - *Solution*: AI for precise pricing, personalized offers, and proactive retention.
  2. **Intelligent Finance** (AI for Credit Scoring):
     - *Problem*: "Unbankable" populations, default prediction errors, manual assessment.
     - *Solution*: Smarter credit risk assessment, inclusive lending, data-driven insights.
  3. **Tax Intelligence** (AI for Fraud Detection):
     - *Problem*: Complex evasion schemes, massive data volumes, audit bias.
     - *Solution*: Identify non-compliance, optimize audit resources, detect fraud.
  4. **Predictive Marketing** (AI for Customer Analytics):
     - *Problem*: Wasted budgets, difficulty targeting, "noise" in digital space.
     - *Solution*: Advanced segmentation, predicting consumer actions, campaign optimization.
  5. **Risk Management** (AI for Risk Intelligence):
     - *Problem*: Reactive methods, dynamic threats (fraud/cyber), regulatory pressure.
     - *Solution*: Proactive identification, assessment, and mitigation of enterprise risks.

=== 4. KEY CAMPAIGNS & TEAMS ===
- **AI in Every City**:
  - Free regional hubs (Nakawa, Soroti, Kabale, Muni/Arua).
  - 900+ applicants.
  - Activities: Python Hackathons, Power BI projects.
- **Team Leadership**:
  - Paul Nesta Katende (CEO), Martin Ayebazibwe (Admin/Ops), Patience Asiimwe (Finance), Bill Dan Arnold Borodi (Media), Julius Basiima (Community).
  - Advisory Board: Daniel Reime, Yasmin Kayali Sabra, Thomas Thorsell-Arntsen, Kenneth Oduka, Dr. Abhishesh Pal.

=== STRICT GUARDRAILS ===
1. **Scope**: Answer ONLY about Otic Foundation, Academy, OIET, and AI education in Uganda. Redirect all else.
2. **Length**: Keep it CONCISE (2-4 bulleted paragraphs).
3. **No**: Code generation, essays, homework, financial/medical advice, politics.
4. **Tone**: Professional, inspiring, community-focused. 🇺🇬
"""

# ============================================
# GUARDRAIL FUNCTIONS
# ============================================

def check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit. Returns True if blocked."""
    current_time = time.time()
    # Clean old requests outside the window
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return True
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return False

def contains_blocked_content(message: str) -> bool:
    """Check if message contains blocked keywords/phrases."""
    message_lower = message.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in message_lower:
            return True
    return False

def truncate_response(text: str, max_length: int = MAX_RESPONSE_LENGTH) -> str:
    """Truncate response to maximum length, ending at a sentence if possible."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Try to end at a sentence
    last_period = truncated.rfind('.')
    last_exclaim = truncated.rfind('!')
    last_question = truncated.rfind('?')
    last_sentence_end = max(last_period, last_exclaim, last_question)
    
    if last_sentence_end > max_length * 0.7:  # Only use if reasonable
        truncated = truncated[:last_sentence_end + 1]
    else:
        truncated = truncated.rstrip() + "..."
    
    return truncated

# ============================================
# CHAT ENDPOINT WITH GUARDRAILS
# ============================================

# ============================================
# CHAT ENDPOINT WITH MEMORY & GUARDRAILS
# ============================================

# In-memory history store: session_id -> list of messages
# Format: {"role": "user/assistant", "content": "..."}
conversation_history = defaultdict(list)
MAX_HISTORY_MESSAGES = 10  # Keep last 10 messages (5 turns)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"  # Optional session ID for memory

@app.post("/chat")
async def chat(request: ChatRequest, req: Request):
    # Get client IP for rate limiting
    client_ip = req.client.host if req.client else "unknown"
    
    # GUARDRAIL 1: Rate Limiting
    if check_rate_limit(client_ip):
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(RATE_LIMIT_RESPONSE)
    
    # GUARDRAIL 2: Keyword Filter
    if contains_blocked_content(request.message):
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(BLOCKED_RESPONSE)
    
    # GUARDRAIL 3: Empty/Too Short Message
    if len(request.message.strip()) < 2:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("Please type a message to get started! Ask me anything about the Otic Foundation. 😊")
    
    # MEMORY: Retrieve and update history
    session_id = request.session_id
    history = conversation_history[session_id]
    
    # Append user message
    history.append({"role": "user", "content": request.message})
    
    # Trim history if too long
    if len(history) > MAX_HISTORY_MESSAGES:
        history = history[-MAX_HISTORY_MESSAGES:]
        conversation_history[session_id] = history

    async def generate():
        try:
            full_response = ""
            
            # Construct messages with system prompt + history
            messages = [{"role": "system", "content": OTIC_CONTEXT}] + history
            
            stream = client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                stream=True,
                max_tokens=1024,  # Increased from 500 to flow better
                temperature=0.7,
            )

            for chunk in stream:
                # CHECK FOR DISCONNECT (Stop generating if user leaves)
                if await req.is_disconnected():
                    break
                    
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Memory: Append assistant response after generation
            if full_response:
                conversation_history[session_id].append({"role": "assistant", "content": full_response})

        except Exception as e:
            yield f"I'm having trouble responding right now. Please try again. (Error: {str(e)})"

    from fastapi.responses import StreamingResponse
    return StreamingResponse(generate(), media_type="text/plain")

# Root endpoint (fixes 404 on Hugging Face health checks)
@app.get("/")
async def root():
    return {
        "name": "OticBot API",
        "version": "1.0",
        "description": "AI Assistant for the Otic Foundation",
        "endpoints": {
            "POST /chat": "Send a message to OticBot",
            "GET /health": "Check API health status"
        },
        "guardrails": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "guardrails": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
