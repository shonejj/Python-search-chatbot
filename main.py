from typing import List
import uvicorn
import re
import json
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from duckduckgo_search import AsyncDDGS

# Initialize FastAPI app
app = FastAPI()

# Model for user details
class UserDetail(BaseModel):
    email: str
    phone: str

# Initialize an empty list to store user details globally
users_list = []

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

def extract_user_details(user_input):
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

def save_user_details(user_details):
    # Load existing user details from JSON file
    try:
        with open('user_details.json', 'r') as json_file:
            users_list = json.load(json_file)
    except FileNotFoundError:
        users_list = []

    # Append new user details
    users_list.append(user_details.dict())

    # Save updated user details to JSON file
    with open('user_details.json', 'w') as json_file:
        json.dump(users_list, json_file, indent=4)

@app.post("/user-details/", response_model=UserDetail)
async def collect_user_details(user_detail: UserDetail):
    save_user_details(user_detail)
    return user_detail

@app.post("/chatbot/")
async def chatbot_interaction(query: str):
    response = await search_web(query)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
