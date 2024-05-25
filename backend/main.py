from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
from PIL import Image
import services as _service


class ImageCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 0
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    model_name: Optional[str] = "CompVis/stable-diffusion-v1-4"

    class Config:
        protected_namespaces = ()

class Img2ImgCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 0
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    model_name: Optional[str] = "CompVis/stable-diffusion-v1-4"

    class Config:
        protected_namespaces = ()


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

@app.post("/api/generate/")
async def generate_image(params: ImageCreate):
    try:
        image = await _service.generate_image(params)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/img2img/")
async def img2img(params: Img2ImgCreate, file: UploadFile = File(...)):
    try:
        input_image = Image.open(file.file).convert("RGB")
        image = await _service.img2img(params, input_image)
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

