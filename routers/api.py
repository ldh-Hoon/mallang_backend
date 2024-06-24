import os, requests
from fastapi import APIRouter, UploadFile, BackgroundTasks, Form, File
from pydantic import BaseModel
from utils.data_control import *
from typing import Optional

from fastapi.responses import Response, FileResponse, JSONResponse
from utils.urls import *
from utils.convert import *
from routers.mallang_tts import tts

standard_wav = "parent/a1.wav"
api = APIRouter(prefix='/api')

class TTS_payload(BaseModel):
    email: str
    text: str
    book: str
    role: str

class TTS_parent_payload(BaseModel):
    email: str
    book: str

def tts_save(email, book_data, file):
    with open(file, 'rb') as f:
        raw = f.read()

    speed = 0.8
    for scene in book_data['script']:
        if scene['role']=='나레이션':
            files = {'wav': raw}
            d = {'text': scene['text'], "speed": 1.0, "email":clean_text(email)}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{email}_{scene["id"]}.mp3', 'wb') as file:
                file.write(res.content)

            files = {'wav': raw}
            d = {'text': scene['text'], "speed": speed, "email":clean_text(email)}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{email}_{scene["id"]}_slow.mp3', 'wb') as file:
                file.write(res.content)
        else:
            files = {'wav': raw}
            d = {'text': scene['text'], "speed": speed, "email":clean_text(email)}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{email}_{scene["id"]}_slow.mp3', 'wb') as file:
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
        
        with open(file, 'rb') as f:
            raw = f.read()
        files = {'wav': raw}
        data = {'text': data.text, "speed": 1.0, "email":clean_text(data.email)}
        res = requests.post(TTS_ENDPOINT2, files=files, data = data)
        with open(f'temp.wav', 'wb') as file:
            file.write(res.content)
        return JSONResponse({"data":encode_audio('temp.wav')})
    else:
        characterId = book_json(data.book)['voice_id'][data.role]

        with open(f"character/{characterId}.mp3", 'rb') as f:
            raw = f.read()
        files = {'wav': raw}
        data = {'text': data.text, "speed":1.0, "email":clean_text(data.email)}
        res = requests.post(TTS_ENDPOINT2, files=files, data = data)

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
    
    background_tasks.add_task(tts_save, data.email, book_data, file)

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

@api.post('/tts_infer') 
async def api(text: str = Form(...), wav: UploadFile = File(...), speed: float = Form(1.0), email: str = Form(...)):
    wav_content = await wav.read()
    email = email
    text = text
    speed = speed
    with open(f"./wavs/input_{email}.wav", "wb") as file:
        file.write(wav_content)
    # loop = asyncio.get_event_loop()
    # await loop.run_in_executor(None, tts, text, speed, f"./wavs/input_{email}.wav", f"./wavs/output_{email}.wav")
    tts(text, speed, f"./wavs/input_{email}.wav", f"./wavs/output_{email}.wav")
    return FileResponse(f"./wavs/output_{email}.wav", filename=f"output_{email}.wav")
