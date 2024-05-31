import uvicorn
from fastapi import FastAPI
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from pydantic import BaseModel
from find import findBus
from env import getEnv
from gemini.run_model import generate_response
origins = [
    # "http://localhost",
    # "http://localhost:3000",
    # "https://dq-hustlecoding.github.io/dqflex",
    # "https://dq-hustlecoding.github.io",
    # "http://api.dqflex.kro.kr:8080",
    # "http://api.dqflex.kro.kr",
    "*",
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

# 환경변수
app = FastAPI(middleware=middleware)


@app.get("/get-destination/{string}")
async def read_goal(string: str = ""):
    result = generate_response(string)
    return {"result": result}


class GetBusResultRequest(BaseModel):
    userLati: float
    userLong: float
    userOrigin: str
    userDestination: str

@app.post("/get-bus-result")
async def get_bus_result(item: GetBusResultRequest):
    # update_prompt(item.userOrigin, item.userDestination)
    return findBus(item.userLati, item.userLong, item.userDestination)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 8000)