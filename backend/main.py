from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
from PIL import Image
import services as _service
from schemas import ImageCreate, Img2ImgCreate
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

@app.post("/api/generate/")
async def generate_image(params: ImageCreate):
    try:
        params.prompt += ",Masterpiece, high_quality,super detail"
        image = await _service.generate_image(params)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/img2img/")
async def img2img(file: UploadFile = File(...), params: str = Form(...)):
    try:
        # JSON 문자열을 파이썬 객체로 변환
        params_dict = json.loads(params)
        img2img_params = Img2ImgCreate(**params_dict)

        input_image = Image.open(file.file).convert("RGB")
        image = await _service.img2img(img2img_params, input_image)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/api/generate_2d_asset/")
async def generate_2d_asset(params: ImageCreate):
    try:
        params.prompt += ",pixel art assets for a rpg videogame +,Masterpiece, high_quality,super detail"
        image = await _service.generate_image(params)
        image = _service.remove_bg(image)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return (StreamingResponse(memory_stream, media_type="image/png"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/generate_withoutbg/")
async def generate_image(params: ImageCreate):
    try:
        params.prompt += ",Masterpiece, high_quality,super detail"
        image = await _service.generate_image(params)
        image = _service.remove_bg(image)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))