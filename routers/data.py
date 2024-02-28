from fastapi import APIRouter, UploadFile
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse, FileResponse

from utils.convert import *
from utils.data_control import *
import os
from utils.urls import *


data_api = APIRouter(prefix='/data')

class File_request_payload(BaseModel):
    email: str
    type: str
    book: Optional[str] = None
    file: Optional[str] = None


@data_api.post("/upload/parent_audio/{email}")
async def upload_audio(file : UploadFile, email):
    content = await file.read()
    with open(f"parent/{clean_text(email)}.aac", 'wb') as file:
        file.write(content)
    convert_aac2wav(f"parent/{clean_text(email)}")
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
        json_data = get_json()
        if json_data['script'][int(payload.file)]['role'] == "나레이션":
            filepath = os.path.join("./books", payload.book, "voices", f"{payload.email}_{payload.file}.mp3")
            if not os.path.isfile(filepath):
                return "fail"
        else:
            filepath = os.path.join("./books", payload.book, "voices", f"{payload.file}.mp3")
        return JSONResponse({"data":encode_audio(filepath)})
    return 'fail'