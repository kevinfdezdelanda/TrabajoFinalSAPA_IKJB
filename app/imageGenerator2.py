from diffusers import AutoPipelineForText2Image
import torch
from PIL import Image

pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("cpu")

prompt = "A cinematic shot of a baby racoon wearing an intricate italian priest robe."

images = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]

# Guardamos la imagen
image_path= "image.jpg"
images.save(image_path, "JPEG")