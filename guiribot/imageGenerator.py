from diffusers import DiffusionPipeline
import torch
from PIL import Image

#pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float32,  # Asegúrate de usar float32 para la CPU
    use_safetensors=True
)


pipe.to("cpu")

# if using torch < 2.0
# pipe.enable_xformers_memory_efficient_attention()

prompt = "An astronaut riding a green horse"

images = pipe(prompt=prompt).images[0]

# Guardamos la imagen
image_path= "image.jpg"
images.save(image_path, "JPEG")