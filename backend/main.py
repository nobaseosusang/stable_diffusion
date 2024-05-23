from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
from PIL import Image
import services as _service
import json

# 데이터 모델 정의
class ImageCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 42
    num_inference_steps: int = 10
    guidance_scale: float = 7.5

class Img2ImgCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 42
    num_inference_steps: int = 10
    guidance_scale: float = 7.5

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

# 텍스트 프롬프트를 기반으로 이미지를 생성하기 위한 엔드포인트
@app.post("/api/generate/")
async def generate_image(params: ImageCreate):
    try:
        # 이미지 생성 서비스 호출
        image = await _service.generate_image(params)

        # 메모리 스트림에 이미지를 저장
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)  # 스트림의 시작 위치로 이동

        # 생성된 이미지를 스트리밍 응답으로 반환
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        # 예외 발생 시 클라이언트에게 오류 메시지 반환
        raise HTTPException(status_code=500, detail=str(e))

# 이미지를 기반으로 이미지를 생성하기 위한 엔드포인트
@app.post("/api/img2img/")
async def img2img(
    prompt: str = Form(...),
    seed: Optional[int] = Form(42),
    num_inference_steps: int = Form(10),
    guidance_scale: float = Form(7.5),
    file: UploadFile = File(...)
):
    try:
        # JSON 데이터를 Img2ImgCreate 모델로 변환
        params = Img2ImgCreate(
            prompt=prompt,
            seed=seed,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        )

        # 업로드된 이미지를 열기
        input_image = Image.open(file.file).convert("RGB")

        # 이미지 생성 서비스 호출
        image = await _service.img2img(params, input_image)

        # 메모리 스트림에 이미지를 저장
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)  # 스트림의 시작 위치로 이동

        # 생성된 이미지를 스트리밍 응답으로 반환
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        # 예외 발생 시 클라이언트에게 오류 메시지 반환
        raise HTTPException(status_code=500, detail=str(e))
