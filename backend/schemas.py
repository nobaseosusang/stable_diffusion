from pydantic import BaseModel
from typing import Optional

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
