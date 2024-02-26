import os, requests
from fastapi import APIRouter, UploadFile, BackgroundTasks
from pydantic import BaseModel
from utils.data_control import *
from typing import Optional

from fastapi.responses import Response, FileResponse, JSONResponse
from utils.urls import *
from utils.convert import *

standard_wav = "parent/a1.wav"
api = APIRouter(prefix='/api')

class TTS_payload(BaseModel):
    email: str
    text: str
    book: str
    role: str
    sleepMode: Optional[int] = 0

class TTS_parent_payload(BaseModel):
    email: str
    book: str
    sleepMode: Optional[int] = 0


def tts_save(book_data, file, mode):
    raw = open(file, 'rb') 

    speed = 1.0    
    if mode == 1:
        speed = 0.8
    for scene in book_data['script']:
        if scene['role']=='나레이션':
            files = {'wav': raw}
            d = {'text': scene['text'], "speed": speed}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{scene["id"]}.mp3', 'wb') as file:
                file.write(res.content)

@api.post('/tts')
async def TTS(data : TTS_payload):
    json_data = get_json()

    if not data.email in json_data:
        return "no email"

    if data.role == '나레이션':
        file = standard_wav
        if os.path.isfile(f"parent/{clean_text(data.email)}.wav"):
            file = f"parent/{clean_text(data.email)}.wav"

        speed = 1.0    
        if data.sleepMode == 1:
            speed = 0.8
        
        raw = open(file, 'rb')
        files = {'wav': raw}
        data = {'text': data.text, "speed": speed}
        res = requests.post(TTS_ENDPOINT, files=files, data = data)
        with open(f'temp.wav', 'wb') as file:
            file.write(res.content)
        return JSONResponse({"data":encode_audio('temp.wav')})
    else:
        characterId = book_json(data.book)['voice_id'][data.role]

        raw = open(f"character/{characterId}.mp3", 'rb')
        files = {'wav': raw}
        data = {'text': data.text}
        res = requests.post(TTS_ENDPOINT, files=files, data = data)

        with open(f'temp.wav', 'wb') as file:
            file.write(res.content)
        return JSONResponse({"data":encode_audio('temp.wav')})
        

@api.post('/tts/prepare')
async def prepare(data : TTS_parent_payload, background_tasks: BackgroundTasks):
    json_data = get_json()

    if not data.email in json_data:
        return 'fail'

    file = f"parent/a1.wav"
    if os.path.isfile(f"parent/{clean_text(data.email)}.wav"):
        file = f"parent/{clean_text(data.email)}.wav"
    book_data = book_json(data.book)
    
    background_tasks.add_task(tts_save, book_data, file, data.mode)

    data = {
        "status":"success"
    }
    return JSONResponse(data)

@api.post('/rvc/{email}/{book}/{role}')
async def prepare(file : UploadFile, email, book, role):
    content = await file.read()
    with open(f"temp_{clean_text(email)}.aac", 'wb') as file:
        file.write(content)
    convert_aac2wav(f"temp_{clean_text(email)}")

    json_data = get_json()
    age = json_data[email]['info']['age']
    gender = 0
    if age==None:
        age = 7
    if json_data[email]['info']['gender'] == '여성':
        gender = 0
    if json_data[email]['info']['gender'] == '남성':
        gender = 1
    
    books = os.listdir('./books')
    if not book in books:
        return "fail"
    characterId = book_json(book)['voice_id'][role]


    files = {'wav': open(f"temp_{clean_text(email)}.wav", 'rb')}
    data = {'CharacterId': characterId,
            'age': age,
            'gender': gender}
    requests.post(f'{RVC_ENDPOINT}/upload', files=files, data=data)

    response = requests.get(f'{RVC_ENDPOINT}/download')
    with open(f'rvc_temp.wav', 'wb') as file:
        file.write(response.content)
    
    return JSONResponse({"data":encode_audio('rvc_temp.wav')})

