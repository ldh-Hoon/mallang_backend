from fastapi import APIRouter, UploadFile, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse, FileResponse

from utils.convert import *
from utils.data_control import *
import os, requests
from utils.urls import *


data_api = APIRouter(prefix='/data')

class File_request_payload(BaseModel):
    email: str
    type: str
    book: Optional[str] = None
    file: Optional[str] = None

def tts_save(book_data, file):
    with open(file, 'rb') as f:
        raw = f.read()
    for scene in book_data['script']:
        if scene['role']=='나레이션':
            files = {'wav': raw}
            d = {'text': scene['text']}
            res = requests.post(TTS_ENDPOINT, files=files, data=d)
            with open(f'books/{book_data["title"]}/voices/{scene["id"]}.mp3', 'wb') as file:
                file.write(res.content)

@data_api.post("/upload/parent_audio/{email}")
async def upload_audio(file : UploadFile, email, background_tasks: BackgroundTasks):
    content = await file.read()
    with open(f"parent/{clean_text(email)}.aac", 'wb') as file:
        file.write(content)
    convert_aac2wav(f"parent/{clean_text(email)}")

    file = f"parent/a1.wav"
    if os.path.isfile(f"parent/{clean_text(email)}.wav"):
        file = f"parent/{clean_text(email)}.wav"
    book_data = book_json("토끼와 거북이")
    
    background_tasks.add_task(tts_save, book_data, file)
    return "ok"

@data_api.get('/{type}/{book}/{filename}')
async def show(type, book, filename):
    if type == 'image':
        return FileResponse(f"books/{book}/img/{filename}.png")
    elif type == 'audio':
        return FileResponse(f"books/{book}/voices/{filename}.mp3")

@data_api.get('/booklist')
async def booklist():
    books = os.listdir('./books')
    return JSONResponse({"books":books})


@data_api.post('/get/file')
async def return_file(payload : File_request_payload):
    if payload.type == "json":
        filepath = os.path.join("./books", payload.book, f"{payload.book}.json")
        if not os.path.isfile(filepath):
            return "fail"
        return FileResponse(filepath)
    
    
    elif payload.type == "image" and payload.book != None and payload.file != None:
        
        filepath = os.path.join("./books", payload.book, "img",f"{payload.file}.png")
        if not os.path.isfile(filepath):
            return "fail"
        
        return FileResponse(filepath)
    
    elif payload.type == "audio" and payload.book != None and payload.file != None:
        
        filepath = os.path.join("./books", payload.book, "voices", f"{payload.file}.mp3")
        if not os.path.isfile(filepath):
            return "fail"
        
        return JSONResponse({"data":encode_audio(filepath)})
    return 'fail'