from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io
from PIL import Image
import services as _service  # service.py 파일을 import

# 데이터 모델 정의
class ImageCreate(BaseModel):
    prompt: str
    seed: Optional[int] = 42
    num_inference_steps: int = 10
    guidance_scale: float = 7.5

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

# 이미지를 생성하기 위한 엔드포인트
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

