from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, Flask, send_from_directory, session, send_file
)
from guiribot.auth import login_required
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, pipeline, Wav2Vec2ForCTC, Wav2Vec2Processor
from diffusers import StableCascadeDecoderPipeline, StableCascadePriorPipeline, StableCascadeUNet
from werkzeug.exceptions import abort
from datasets import load_dataset
import torch
import torchaudio
import soundfile as sf
import time
import os
from guiribot.auth import login_required
from guiribot.db import get_db
from pydub import AudioSegment
from pathlib import Path

bp = Blueprint('chatbot', __name__)

# Define el nombre del modelo que se va a utilizar. En este caso, es 'facebook/blenderbot-400M-distill'
model_name = 'facebook/blenderbot-400M-distill'

# Crea una instancia del tokenizador para BlenderBot a partir del modelo preentrenado.
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)

# Carga el modelo de generación condicional de BlenderBot a partir del modelo preentrenado.
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

# Carga el procesador del modelo de reconocimiento de voz
processor_speechrecognition = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")

# Carga el modelo de reconocimiento de voz
model_speechrecognition = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Descarga el modelo de síntesis de voz a través de pipeline
synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")

# Descarga el dataset de embeddings de voces
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

# Índice del embedding de voz utilizado
voz = 5000

# Conversión de embedding de voz a tensor de PyTorch
speaker_embedding = torch.tensor(embeddings_dataset[voz]["xvector"]).unsqueeze(0)

# Palabras prohibidas
prohibited_keywords = [
    "idiot", "moron", "dumb", "stupid", "imbecile", "fool", "jerk", "asshole", "retard", "twat",
    "racist", "nazi", "bigot", "supremacist", "xenophobe", "klansman", "ethnocentric", "jingoist", "racial", "sectarian",
    "faggot", "dyke", "tranny", "homophobic", "queer", "sissy", "transphobe", "gaylord", "heterosexist", "gender-biased",
    "fuck", "sex", "porn", "masturbate", "dick", "vagina", "whore", "slut", "orgasm", "ejaculate",
    "kill", "murder", "terrorist", "bomb", "assassinate", "shoot", "stab", "massacre", "slaughter", "mutilate",
    "cocaine", "heroin", "meth", "LSD", "ecstasy", "marijuana", "amphetamine", "opium", "ketamine", "morphine",
    "steal", "fraud", "corruption", "burglary", "embezzle", "smuggle", "launder", "trespass", "hack", "bribe",
    "extremist", "hate speech", "radical", "terrorist", "fanatic", "extremism", "hateful", "militant", "insurgent", "radicalize",
    "slander", "libel", "defame", "harass", "stalk", "invade privacy", "blackmail", "smear", "discredit", "expose",
    "bitch", "bastard", "pimp", "hoe", "gangster", "thug", "scum", "shithead", "douchebag", "prick",
]

@bp.route('/')
@login_required
def index():
    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    return render_template('chatbot/index.html')

# La idea es que el usuario pueda introducir tanto texto como voz y que la respuesta del chat sea siempre igual,
# mostrando la respuesta en texto y reproduciendo por voz.

# generate_response_and_audio() -> Método común para ambos casos. Recibe un texto y generea la respuesta en texto y audio y la manda al back
# get_bot_response() -> Para cuando el usuario pregunta por texto. Se recibe el texto por GET y lo manda a generate_response_and_audio()
# upload_audio() -> Para cuando el usuario pregunta por voz. Recibe el fichero de audio por POST, lo procesa, y cuando obtiene la transcripción llama a generate_response_and_audio().

@bp.route('/get')  # Define una ruta en el servidor web que escucha las solicitudes GET en la URL '/get'.
def get_bot_response():  # Define la función que maneja las solicitudes en esta ruta.
    user_input = request.args.get('msg')  # Obtiene el mensaje del usuario desde los argumentos de la URL.
    return generate_response_and_audio(user_input)

# Función que obtiene una pregunta al chatbot en string y genera la respuesta para el fronts
def generate_response_and_audio(user_input):
    # Verifica si el mensaje del usuario contiene alguna palabra prohibida.
    if any(keyword in user_input.lower() for keyword in prohibited_keywords):
        # Si encuentra una palabra prohibida, devuelve un mensaje de error.
        return "I'm sorry, but I prefer not to talk about these topics."

    # Prepara el mensaje del usuario para el modelo transformándolo en el formato adecuado.
    inputs = tokenizer([user_input], return_tensors='pt')

    # Pasa el mensaje procesado al modelo y genera una respuesta.
    result = model.generate(**inputs, max_length=40)

    # Decodifica la respuesta generada por el modelo para convertirla en texto legible.
    reply = tokenizer.decode(result[0], skip_special_tokens=True)

    # Transforma el texto obtenido del chatbot a voz
    speech = synthesiser(reply, forward_params={"speaker_embeddings": speaker_embedding})

    # Timestamp, reemplazando el punto por -
    ts = str(time.time()).replace(".", "-")
    
    # Obtención del nombre de usuario
    username = session.get("username")

    # Construcción de la ruta del fichero
    filepath = Path(f"guiribot/wav") / f"{username}-{ts}.wav"

    # Guardado del fichero de salida
    sf.write(filepath, speech["audio"], samplerate=speech["sampling_rate"])

    # Devuelve la respuesta del chatbot y la ruta al fichero de voz en formato JSON.
    # También devuelve el texto de entrada. Redundante para cuando la entrada es texto, necesario cuando la entrada es por voz.
    return jsonify({"text": reply, "audio": filepath.as_posix(), "transcription": user_input})

# Maneja las peticiones de obtención de ficheros WAV.
@bp.route('/guiribot/wav/<path:filename>')
def serve_wav(filename):
    return send_from_directory('wav', filename)

# Maneja las peticiones de obtención de imagenes.
@bp.route('/guiribot/imagenes/<path:filename>')
def serve_image(filename):
    return send_from_directory('imagenes', filename)

# Función que maneja la subida de audio al servidor y hace el reconocimiento de voz
@bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    
    # Comprueba que haya un fichero en la petición
    if 'audio' in request.files:
        audio = request.files['audio']
        
        # Nombre del fichero obtenido sin procesar
        filename = audio.filename
        
        # Ruta al fichero
        filepath = Path("guiribot/wav/in") / filename
        
        # Guarda el archivo original
        audio.save(filepath)
        
        # Abre el fichero guardado
        audio = AudioSegment.from_file(filepath, format="webm")
        
        # Ruta al fichero nuevo convertido
        filepath = Path("guiribot/wav/in/transformed") / filename
        
        # Transforma el fichero original a WAV
        audio.export(filepath, format="wav")
        
        # Se establece la tasa de muestreo. Son como los FPS pero de audio.
        target_sampling_rate = 16_000
    
        # Se carga el fichero transformado
        waveform, sampling_rate = torchaudio.load(filepath)
        
        # Si la tasa de muestreo del fichero no es la misma que la que acepta el modelo,
        if sampling_rate != target_sampling_rate:
            
            # entonces se remuestrea.
            resampler = torchaudio.transforms.Resample(orig_freq=sampling_rate, new_freq=target_sampling_rate)
            waveform = resampler(waveform)
        
        # Se define el input, se procesa el fichero antes de pasarlo por el modelo
        inputs = processor_speechrecognition(waveform.squeeze(0), return_tensors="pt", sampling_rate=16_000).input_values
        
        # Se realiza la inferencia/predicción
        with torch.no_grad():
            logits = model_speechrecognition(inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        
        # Se obtiene la transcripción
        transcription = processor_speechrecognition.batch_decode(predicted_ids)[0]

        # Se utiliza la transcripción como entrada para el chatbot
        return generate_response_and_audio(transcription.capitalize())
        
    else:
        return jsonify({'error': 'No se encontró el archivo de audio en la solicitud'}), 400
    
@bp.route('/generate-image', methods=['POST'])
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

    # Timestamp, reemplazando el punto por -
    ts = str(time.time()).replace(".", "-")
    
    # Obtención del nombre de usuario
    username = session.get("username")

    # Ejemplo de cómo guardar y enviar la imagen generada
    image_path = Path("guiribot/imagenes") / f"{username}-{ts}.png"  # Asegúrate de especificar la ruta correcta
    decoder_output.save(image_path)
    
    #return send_file(image_path, mimetype='image/png')
    return {'image_url': image_path.as_posix()}

# Verifica si el script se ejecuta como programa principal y no como módulo importado.
if __name__ == "__main__":
    # Ejecuta la aplicación Flask en modo de depuración.
    bp.run(debug=True)