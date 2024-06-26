from fastapi import APIRouter, BackgroundTasks
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from utils.data_control import *
from fastapi.responses import JSONResponse, FileResponse
import requests
from utils.urls import *

class Login_payload(BaseModel):
    email: str
    password: str

class Register_payload(BaseModel):
    password: str
    name: str
    email: str
    age: str
    gender: str
    
class Data_add_payload(BaseModel):
    password: str
    name: str
    email: str
    age: str
    gender: str


account = APIRouter(prefix='/account')

@account.post('/login')
async def login(data: Login_payload, background_tasks: BackgroundTasks):
    if login_check(data.email, data.password):
        file = f"parent/a1.wav"
        if os.path.isfile(f"parent/{clean_text(data.email)}.wav"):
            file = f"parent/{clean_text(data.email)}.wav"        
        
        return "success"
    
    return "fail"

@account.post('/register')
async def register(data: Register_payload):
    if add_account(data.email, data.password, data.name):
        add_data(data.name, data.email, data.age, data.gender)
        return "success"
    return "fail"

@account.post('/update')
async def update(data: Data_add_payload):
    if add_data(data.name, data.email, data.age, data.gender):
        return "success"
    return "fail"

@account.get('/get/{user}')
async def get_data(user):
    data = get_json()
    if user in data:
        return JSONResponse(data[user]['info'])
    return "fail"


