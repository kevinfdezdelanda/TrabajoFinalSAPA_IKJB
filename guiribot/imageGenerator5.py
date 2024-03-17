
from flask import Flask, request, send_file
import torch
from diffusers import StableCascadeDecoderPipeline, StableCascadePriorPipeline, StableCascadeUNet

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():

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

    data = request.json
    prompt = data['prompt']

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
        
    # Aquí incluyes tu lógica actual de generación de imágenes utilizando el prompt recibido
    # Usando el código que ya tienes en imageGenerator5.py pero asegurándote de utilizar el prompt recibido
    # Al final, guardas la imagen generada y la devuelves como respuesta

    # Ejemplo de cómo guardar y enviar la imagen generada
    image_path = "guiribot/imagenes/image.png"  # Asegúrate de especificar la ruta correcta
    decoder_output.save(image_path)
    
    return send_file(image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

