from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Load API key
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-70b-8192"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

app = FastAPI()

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow frontend requests (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    user_input: str

# Home route → load app.html
@app.get("/")
def home():
    return FileResponse(os.path.join("static", "app.html"))

@app.post("/generate-plan")
def generate_plan(req: RequestBody):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant that designs structured learning plans."},
            {"role": "user", "content": f"Create a detailed AI curriculum for: {req.user_input}"}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return {"curriculum": data['choices'][0]['message']['content']}
    
    except requests.exceptions.HTTPError:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
