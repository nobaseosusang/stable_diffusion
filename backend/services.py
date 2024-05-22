from pathlib import Path 
import schemas as _schemas
import torch 
from diffusers import StableDiffusionPipeline
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# HuggingFace 토큰 가져오기
"""
참고: .env 파일이 존재하고, 그 파일에 토큰이 포함되어 있어야 합니다.
"""
HF_TOKEN = os.getenv('HF_TOKEN')

# 파이프라인 생성
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", 
    revision="fp16", 
    torch_dtype=torch.float16,
    use_auth_token=HF_TOKEN
)

# 사용할 장치 설정
if torch.backends.mps.is_available():
    device = "mps"
else: 
    device = "cuda" if torch.cuda.is_available() else "cpu"

pipe.to(device)

# 이미지 생성 함수
async def generate_image(imgPrompt: _schemas.ImageCreate) -> Image: 
    generator = None if imgPrompt.seed is None else torch.Generator(device=device).manual_seed(int(imgPrompt.seed))

    image: Image = pipe(
        imgPrompt.prompt,
        guidance_scale=imgPrompt.guidance_scale, 
        num_inference_steps=imgPrompt.num_inference_steps, 
        generator=generator
    ).images[0]
    
    return image
