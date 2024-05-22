from fastapi import FastAPI, HTTPException, Depends, Query, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import Optional
import pydantic as _pydantic
import io
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch

# 데이터 모델 정의
class _PromptBase(_pydantic.BaseModel):
    seed: Optional[int] = 42
    num_inference_steps: int = 10
    guidance_scale: float = 7.5

class ImageCreate(_PromptBase):
    prompt: str

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# Stable Diffusion 파이프라인 로드 (미리 로드하여 성능 향상)
model_id = "CompVis/stable-diffusion-v1-4"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16).to("cuda")

@app.get("/")
def read_root():
    return {"message": "Stable Diffusers API에 오신 것을 환영합니다"}

@app.get("/api")
async def root():
    return {"message": "FastAPI를 사용한 Stable Diffusers 데모에 오신 것을 환영합니다"}

# 이미지를 생성하기 위한 엔드포인트
@app.get("/api/generate/")
async def generate_image(
    prompt: str = Query(..., description="이미지를 생성할 텍스트 프롬프트"),
    seed: Optional[int] = Query(42, description="출력이 결정론적이 되도록 하는 시드 값"),
    guidance_scale: float = Query(7.5, description="프롬프트에 더 잘 맞는 이미지를 생성하도록 하는 가이드 스케일"),
    num_inference_steps: int = Query(10, description="노이즈 제거 단계의 수")
):
    # 쿼리 매개변수를 ImageCreate 모델로 변환
    imgPromptCreate = ImageCreate(
        prompt=prompt,
        seed=seed,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps
    )
    
    try:
        # 이미지 생성 서비스 호출
        image = await generate_image_service(imgPromptCreate)

        # 메모리 스트림에 이미지를 저장
        memory_stream = io.BytesIO()
        image.save(memory_stream, format="PNG")
        memory_stream.seek(0)  # 스트림의 시작 위치로 이동

        # 생성된 이미지를 스트리밍 응답으로 반환
        return StreamingResponse(memory_stream, media_type="image/png")
    except Exception as e:
        # 예외 발생 시 클라이언트에게 오류 메시지 반환
        raise HTTPException(status_code=500, detail=str(e))

# HTML 폼을 제공하는 엔드포인트
@app.get("/form", response_class=HTMLResponse)
def form():
    return """
        <html>
            <head>
                <title>Generate Image</title>
            </head>
            <body>
                <h1>Generate Image with Stable Diffusion</h1>
                <form action="/submit_form" method="post">
                    <label for="prompt">Prompt:</label>
                    <input type="text" id="prompt" name="prompt" required><br><br>
                    <label for="seed">Seed:</label>
                    <input type="number" id="seed" name="seed" value="42"><br><br>
                    <label for="guidance_scale">Guidance Scale:</label>
                    <input type="number" step="0.1" id="guidance_scale" name="guidance_scale" value="7.5"><br><br>
                    <label for="num_inference_steps">Number of Inference Steps:</label>
                    <input type="number" id="num_inference_steps" name="num_inference_steps" value="10"><br><br>
                    <input type="submit" value="Generate">
                </form>
            </body>
        </html>
    """

# 폼 입력을 처리하고 이미지를 생성하는 엔드포인트
@app.post("/submit_form")
async def submit_form(
    prompt: str = Form(...),
    seed: Optional[int] = Form(42),
    guidance_scale: float = Form(7.5),
    num_inference_steps: int = Form(10)
):
    imgPromptCreate = ImageCreate(
        prompt=prompt,
        seed=seed,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps
    )
    
    try:
        # 이미지 생성 서비스 호출
        image = await generate_image_service(imgPromptCreate)

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
async def generate_image_service(imgPrompt: ImageCreate) -> Image:
    # Stable Diffusion을 사용하여 이미지를 생성하는 로직 구현
    generator = torch.manual_seed(imgPrompt.seed)  # 시드 설정
    image = pipe(imgPrompt.prompt, num_inference_steps=imgPrompt.num_inference_steps, guidance_scale=imgPrompt.guidance_scale, generator=generator)["sample"][0]
    
    # PIL 이미지로 변환
    image = image.convert("RGB")
    
    return image
