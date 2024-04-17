from fastapi import FastAPI
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()

url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(url, key)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/nodes")
async def read_items():
    data = supabase.table("nodes").select("NODE_NM").execute()
    return data.data
