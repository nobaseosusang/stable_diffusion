from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch

# 데이터 모델 정의
class ImageCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 42
    num_inference_steps: int = 10
    guidance_scale: float = 7.5

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# Stable Diffusion 파이프라인 로드 (미리 로드하여 성능 향상)
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

# 이미지를 생성하기 위한 엔드포인트
@app.post("/api/generate/")
async def generate_image(params: ImageCreate):
    try:
        # 이미지 생성 서비스 호출
        image = await generate_image_service(params)

        # 메모리 스트림에 이미지를 저장
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)  # 스트림의 시작 위치로 이동

        # 생성된 이미지를 스트리밍 응답으로 반환
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        # 예외 발생 시 클라이언트에게 오류 메시지 반환
        raise HTTPException(status_code=500, detail=str(e))

# 이미지 생성 서비스 함수
async def generate_image_service(params: ImageCreate) -> Image:
    # Stable Diffusion을 사용하여 이미지를 생성하는 로직 구현
    generator = torch.manual_seed(params.seed)  # 시드 설정
    image = pipe(
        params.prompt, 
        num_inference_steps=params.num_inference_steps, 
        guidance_scale=params.guidance_scale, 
        generator=generator
    )["sample"][0]
    
    # PIL 이미지로 변환
    image = image.convert("RGB")
    
    return image

