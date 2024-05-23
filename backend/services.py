from pathlib import Path
import schemas as _schemas
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

# HuggingFace 토큰 가져오기
HF_TOKEN = os.getenv('HF_TOKEN')

# 텍스트 기반 이미지 생성 파이프라인 생성
text_pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", 
    revision="fp16", 
    torch_dtype=torch.float16,
    use_auth_token=HF_TOKEN
)

# 이미지 기반 이미지 생성 파이프라인 생성
img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
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

text_pipe.to(device)
img2img_pipe.to(device)

# 텍스트 기반 이미지 생성 함수
async def generate_image(imgPrompt: _schemas.ImageCreate) -> Image: 
    generator = None if imgPrompt.seed is None else torch.Generator(device=device).manual_seed(int(imgPrompt.seed))

    image: Image = text_pipe(
        imgPrompt.prompt,
        guidance_scale=imgPrompt.guidance_scale, 
        num_inference_steps=imgPrompt.num_inference_steps, 
        generator=generator
    ).images[0]
    
    return image

# 이미지 기반 이미지 생성 함수
async def img2img(imgPrompt: _schemas.Img2ImgCreate, init_image: Image) -> Image:
    generator = None if imgPrompt.seed is None else torch.Generator(device=device).manual_seed(int(imgPrompt.seed))

    image: Image = img2img_pipe(
        prompt=imgPrompt.prompt,
        image=init_image,  # 이미지 인자를 추가
        strength=0.75,  # Strength 파라미터 조절 가능
        guidance_scale=imgPrompt.guidance_scale,
        num_inference_steps=imgPrompt.num_inference_steps,
        generator=generator
    ).images[0]

    return image
