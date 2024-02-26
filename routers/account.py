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
    phoneNumber: str
    age: str
    gender: str
    interests: str
    
class Data_add_payload(BaseModel):
    password: str
    name: str
    email: str
    phoneNumber: str
    age: str
    gender: str
    interests: str


def tts_save(book_data, file):
    with open(file, 'rb') as f:
        raw = f.read()

    speed = 0.8
    for scene in book_data['script']:
        if scene['role']=='나레이션':
            files = {'wav': raw}
            d = {'text': scene['text'], "speed": 1.0}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{scene["id"]}.mp3', 'wb') as file:
                file.write(res.content)

            files = {'wav': raw}
            d = {'text': scene['text'], "speed": speed}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{scene["id"]}_slow.mp3', 'wb') as file:
                file.write(res.content)
        else:
            files = {'wav': raw}
            d = {'text': scene['text'], "speed": speed}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{scene["id"]}_slow.mp3', 'wb') as file:
                file.write(res.content)

account = APIRouter(prefix='/account')

@account.post('/login')
async def login(data: Login_payload, background_tasks: BackgroundTasks):
    if login_check(data.email, data.password):
        file = f"parent/a1.wav"
        if os.path.isfile(f"parent/{clean_text(data.email)}.wav"):
            file = f"parent/{clean_text(data.email)}.wav"
        book_data = book_json("토끼와 거북이")
        
        background_tasks.add_task(tts_save, book_data, file)
        return "success"
    
    return "fail"

@account.post('/register')
async def register(data: Register_payload):
    if add_account(data.email, data.password, data.name):
        add_data(data.name, data.email, data.phoneNumber, data.interests, data.age, data.gender)
        return "success"
    return "fail"

@account.post('/update')
async def update(data: Data_add_payload):
    if add_data(data.name, data.email, data.phoneNumber, data.interests, data.age, data.gender):
        return "success"
    return "fail"

@account.get('/get/{user}')
async def get_data(user):
    data = get_json()
    if user in data:
        return JSONResponse(data[user]['info'])
    return "fail"


