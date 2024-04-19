from fastapi import FastAPI
import os

from supabase import create_client, Client
from dotenv import load_dotenv

from gemini.single_turn import generate_response
from env import getEnv

# 환경변수
app = FastAPI()

url: str = getEnv("SUPABASE_URL")
key: str = getEnv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/nodes")
async def read_items():
    data = supabase.table("nodes").select("NODE_NM").execute()
    return data.data


@app.get("/gimini")
async def read_goal(input: str = ""):
    result = generate_response(input)
    return result
