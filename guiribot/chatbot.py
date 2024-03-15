from flask import (
Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, Flask, send_from_directory, session
)
from guiribot.auth import login_required
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, pipeline, Wav2Vec2ForCTC, Wav2Vec2Processor
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
voz = 33

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

@bp.route('/get')  # Define una ruta en el servidor web que escucha las solicitudes GET en la URL '/get'.
def get_bot_response():  # Define la función que maneja las solicitudes en esta ruta.
    user_input = request.args.get('msg')  # Obtiene el mensaje del usuario desde los argumentos de la URL.
    return generate_response_and_audio(user_input)

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
    
    username = session.get("username")

    # Nombre del fichero de salida
    nombre_fichero = f"guiribot/wav/{username}-{ts}.wav"

    # Guardado del fichero de salida
    sf.write(nombre_fichero, speech["audio"], samplerate=speech["sampling_rate"])

    # Devuelve la respuesta del chatbot y la ruta al fichero de voz en formato JSON.
    return jsonify({"text": reply, "audio": nombre_fichero, "transcription": user_input})

# Maneja las peticiones de obtención de ficheros WAV.
@bp.route('/guiribot/wav/<path:filename>')
def serve_wav(filename):
    return send_from_directory('wav', filename)

# Función que maneja la subida de audio al servidor y hace el reconocimiento de voz
@bp.route('/upload_audio', methods=['POST'])
def upload_audio():
    
    # Comprueba que haya un fichero en la petición
    if 'audio' in request.files:
        audio = request.files['audio']
        
        # Directiorio de destino
        save_path = 'guiribot\\wav\\in'
        
        filename = audio.filename

        # Construcción de la ruta completa, incluido el nombre del fichero
        filepath = os.path.join(save_path, filename)
        
        # Guarda el archivo original
        audio.save(filepath)
        
        # Abre el fichero original
        audio = AudioSegment.from_file(filepath, format="webm")
        
        # Directiorio de destino del fichero transformado
        save_path = 'guiribot\\wav\\in\\transformed'

        # Construcción de la ruta completa al fichero transformado
        filepath = os.path.join(save_path, filename)
        
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

# Verifica si el script se ejecuta como programa principal y no como módulo importado.
if __name__ == "__main__":
    # Ejecuta la aplicación Flask en modo de depuración.
    bp.run(debug=True)