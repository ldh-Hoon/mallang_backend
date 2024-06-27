from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from routers.api import *
from routers.account import account
from routers.data import data_api
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 특정 출처만 허용하려면 출처의 리스트를 사용하세요.
    allow_credentials=True,
    allow_methods=["*"],  # 특정 HTTP 메소드만 허용하려면 메소드의 리스트를 사용하세요.
    allow_headers=["*"],
)

app.include_router(api)
app.include_router(account)
app.include_router(data_api)


@app.get("/")
async def home():
    
    return "Hello!"

@app.get("/hello/{user}")
async def home(user):
    
    return f"Hello! {user}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port = 8000)

