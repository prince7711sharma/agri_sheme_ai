import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from app.prompt import scheme_prompt, insurance_prompt, loan_prompt

load_dotenv()

app = FastAPI(title="Agri Government & Support AI")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def clean(text):
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)
    return text.strip()


# -------- SCHEME --------
class SchemeReq(BaseModel):
    state: str
    land_size: str
    crop: str
    season: str
    language: str

@app.post("/scheme")
def scheme_ai(data: SchemeReq):
    prompt = scheme_prompt(data.dict())
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return {"reply": clean(res.choices[0].message.content)}


# -------- INSURANCE --------
class InsuranceReq(BaseModel):
    crop: str
    season: str
    risk: str
    language: str

@app.post("/insurance")
def insurance_ai(data: InsuranceReq):
    prompt = insurance_prompt(data.dict())
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return {"reply": clean(res.choices[0].message.content)}


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
def loan_ai(data: LoanReq):
    prompt = loan_prompt(data.dict())

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return {
        "reply": clean(res.choices[0].message.content),
        "language": data.language,
        "source": "AI"
    }
