from pydantic import BaseModel, ConfigDict
from typing import Optional
import os
from datetime import datetime
from PIL import Image

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

def save_image_locally(image: Image, output_dir: str = "generated_images") -> str:
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"{output_dir}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    image.save(file_name)
    return file_name