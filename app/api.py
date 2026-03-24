import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware
from app.prompt import scheme_prompt, insurance_prompt, loan_prompt

# Load env
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

# App init
app = FastAPI(title="Agri AI API")

# ✅ CORS (VERY IMPORTANT for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev (React). Later restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq client
client = Groq(api_key=GROQ_API_KEY)


# -------- Utility --------
def clean(text: str) -> str:
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    return text.strip()


def generate_response(prompt: str):
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return clean(res.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- Root --------
@app.get("/")
def root():
    return {"message": "Agri AI API Running 🚀"}


# -------- SCHEME --------
class SchemeReq(BaseModel):
    state: str
    land_size: str
    crop: str
    season: str
    language: str


@app.post("/scheme")
async def scheme_ai(data: SchemeReq):
    prompt = scheme_prompt(data.dict())
    reply = generate_response(prompt)

    return {
        "success": True,
        "data": {
            "reply": reply,
            "type": "scheme",
            "language": data.language
        }
    }


# -------- INSURANCE --------
class InsuranceReq(BaseModel):
    crop: str
    season: str
    risk: str
    language: str


@app.post("/insurance")
async def insurance_ai(data: InsuranceReq):
    prompt = insurance_prompt(data.dict())
    reply = generate_response(prompt)

    return {
        "success": True,
        "data": {
            "reply": reply,
            "type": "insurance",
            "language": data.language
        }
    }


# -------- LOAN --------
class LoanReq(BaseModel):
    purpose: str
    land_owned: bool
    state: str
    district: str
    crop: str
    farmer_type: str
    existing_loan: bool
    language: str


@app.post("/loan")
async def loan_ai(data: LoanReq):
    prompt = loan_prompt(data.dict())
    reply = generate_response(prompt)

    return {
        "success": True,
        "data": {
            "reply": reply,
            "type": "loan",
            "language": data.language,
            "source": "AI"
        }
    }