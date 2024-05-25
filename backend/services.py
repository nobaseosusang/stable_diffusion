from pathlib import Path
import schemas as _schemas
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from safetensors.torch import load_file
from PIL import Image
import os
from dotenv import load_dotenv
import numpy as np
import cv2
import matplotlib.pyplot as plt

load_dotenv()


if torch.backends.mps.is_available():
    device = "mps"
else: 
    device = "cuda" if torch.cuda.is_available() else "cpu"


def remove_bg(image: Image) -> Image:
    # 이미지를 numpy 배열로 변환
    image_np = np.array(image.convert("RGB"))
    
    # 초기 마스크 생성
    mask = np.zeros(image_np.shape[:2], np.uint8)
    
    # GrabCut에 필요한 임시 배열 생성
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    
    # 사각형 ROI 설정 (이미지의 대부분을 포함하도록 설정)
    rect = (10, 10, image_np.shape[1]-10, image_np.shape[0]-10)
    
    # GrabCut 알고리즘 적용
    cv2.grabCut(image_np, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    
    # 배경과 전경을 분리
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    image_np = image_np * mask2[:, :, np.newaxis]
    
    # 알파 채널 추가
    alpha_channel = mask2 * 255
    image_rgba = cv2.cvtColor(image_np, cv2.COLOR_RGB2RGBA)
    image_rgba[:, :, 3] = alpha_channel
    
    # numpy 배열을 다시 PIL 이미지로 변환
    result_image = Image.fromarray(image_rgba)
    return result_image

def load_safetensors_model(model_path):
    state_dict = load_file(model_path)
    return state_dict


async def generate_image(imgPrompt: _schemas.ImageCreate) -> Image:
    model_name_or_path = imgPrompt.model_name
    if model_name_or_path.endswith('.safetensors'):
        state_dict = load_safetensors_model(model_name_or_path)
        pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", state_dict=state_dict)
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
    pipe.to(device)
    
    generator = None if imgPrompt.seed == 0 else torch.Generator(device=device).manual_seed(int(imgPrompt.seed))
    image: Image = pipe(
        imgPrompt.prompt,
        guidance_scale=imgPrompt.guidance_scale, 
        num_inference_steps=imgPrompt.num_inference_steps, 
        generator=generator
    ).images[0]
    return image


async def img2img(imgPrompt: _schemas.Img2ImgCreate, init_image: Image) -> Image:
    model_name_or_path = imgPrompt.model_name
    if model_name_or_path.endswith('.safetensors'):
        state_dict = load_safetensors_model(model_name_or_path)
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained("CompVis/stable-diffusion-v1-4", state_dict=state_dict)
    else:
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
    pipe.to(device)
    
    generator = None if imgPrompt.seed == 0 else torch.Generator(device=device).manual_seed(int(imgPrompt.seed))
    image: Image = pipe(
        prompt=imgPrompt.prompt,
        image=init_image,
        strength=0.75,  # Strength 파라미터 조절 가능
        guidance_scale=imgPrompt.guidance_scale,
        num_inference_steps=imgPrompt.num_inference_steps,
        generator=generator
    ).images[0]
    
    return image
