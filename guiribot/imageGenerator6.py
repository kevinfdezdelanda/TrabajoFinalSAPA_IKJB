
import torch
from diffusers import (
    StableCascadeDecoderPipeline,
    StableCascadePriorPipeline,
    StableCascadeUNet,
)

device = torch.device("cpu")

# Cargar modelos directamente a la CPU sin especificar revisiones fp16
prior_unet = StableCascadeUNet.from_pretrained("stabilityai/stable-cascade-prior", subfolder="prior_lite").to(device)
decoder_unet = StableCascadeUNet.from_pretrained("stabilityai/stable-cascade", subfolder="decoder_lite").to(device)

prior = StableCascadePriorPipeline.from_pretrained("stabilityai/stable-cascade-prior", prior=prior_unet, device=device)
decoder = StableCascadeDecoderPipeline.from_pretrained("stabilityai/stable-cascade", decoder=decoder_unet, device=device)

# Nota: enable_model_cpu_offload es útil para ahorrar memoria cuando se trabaja con modelos grandes en CPU,
# pero puede ralentizar la inferencia debido a la carga y descarga de modelos.
#prior.enable_model_cpu_offload()
#decoder.enable_model_cpu_offload()



prompt = "An astronaut riding a green horse" # Aqui hay que introcucir el texto que se recoge del imput de texto de index.html

negative_prompt = ""

prior_output = prior(
    prompt=prompt,
    height=512,  # Ajuste para compatibilidad y rendimiento en CPU
    width=512,
    negative_prompt=negative_prompt,
    guidance_scale=7.5,
    num_images_per_prompt=1,
    num_inference_steps=20
)

decoder_output = decoder(
    image_embeddings=prior_output.image_embeddings,
    prompt=prompt,
    negative_prompt=negative_prompt,
    guidance_scale=7.5,
    output_type="pil",
    num_inference_steps=50
).images[0]


decoder_output.save("Astronauta2.png")
print("Imagen guardada.")


