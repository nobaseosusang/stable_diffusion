from pathlib import Path
import schemas as _schemas
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from safetensors.torch import load_file
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()


if torch.backends.mps.is_available():
    device = "mps"
else: 
    device = "cuda" if torch.cuda.is_available() else "cpu"


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
