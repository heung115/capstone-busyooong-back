import uvicorn
from fastapi import FastAPI
from supabase import create_client, Client
from single_turn import generate_response
from single_turn import update_prompt
from pydantic import BaseModel
from find import findBus
from env import getEnv

# 환경변수
app = FastAPI()


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
    update_prompt(item.userOrigin, item.userDestination)
    return findBus(item.userLati, item.userLong, item.userDestination)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 8000)