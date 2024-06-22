from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import re
import asyncio

from duckduckgo_search import AsyncDDGS
from database import SessionLocal, engine, Base
from models import UserDetails

# Initialize FastAPI
app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# User input model
class UserInput(BaseModel):
    email: EmailStr
    phone: str

# Extract user details function
def extract_user_details(user_input: str):
    user_details = {"email": "", "phone": ""}
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, user_input)
    if email_matches:
        user_details["email"] = email_matches[0]
    
    # Extract phone number
    phone_pattern = r'\b\d{10}\b'
    phone_matches = re.findall(phone_pattern, user_input)
    if phone_matches:
        user_details["phone"] = phone_matches[0]
    
    return user_details

# Save user details to database
def save_user_details(email: str, phone: str):
    db = SessionLocal()
    user = UserDetails(email=email, phone=phone)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

# DuckDuckGo search function
async def aget_results(query):
    async with AsyncDDGS() as ddgs:
        results = await ddgs.atext(query, max_results=1)
        if results:
            return results[0].get('body', 'No summary available.')
        return 'No summary available.'

async def search_web(query):
    try:
        result = await aget_results(query)
        return result
    except Exception as e:
        return str(e)

# FastAPI endpoint to handle user details input
@app.post("/user_details/")
async def get_user_details(email: str = Form(...), phone: str = Form(...)):
    if not re.match(r'\b\d{10}\b', phone):
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    save_user_details(email, phone)
    return {"message": "Thank you for providing your details!"}

# FastAPI endpoint to handle user queries
@app.post("/query/")
async def handle_query(query: str):
    response = await search_web(query)
    return {"response": response}
