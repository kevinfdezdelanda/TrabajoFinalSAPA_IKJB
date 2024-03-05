from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, Flask, send_from_directory
)
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration, pipeline
from werkzeug.exceptions import abort
from datasets import load_dataset
import torch
import soundfile as sf
import time
from urllib.parse import quote

# from app.auth import login_required
from app.db import get_db

bp = Blueprint('chatbot', __name__)


# Define el nombre del modelo que se va a utilizar. En este caso, es 'facebook/blenderbot-400M-distill'
model_name = 'facebook/blenderbot-400M-distill'
# Crea una instancia del tokenizador para BlenderBot a partir del modelo preentrenado.
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
# Carga el modelo de generación condicional de BlenderBot a partir del modelo preentrenado.
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

# Síntesis voz

# Modelo descargado por pipeline
synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
# Datasets de voces
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
# Índice del embedding de voz utilizado
voz = 5000
# Voz embedding a tensor
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
    
    # Voz
    speech = synthesiser(reply, forward_params={"speaker_embeddings": speaker_embedding})
    
    ts = str(time.time()).replace(".", "-")
    
    nombre_fichero = f"app/wav/{ts}.wav"
    
    sf.write(nombre_fichero, speech["audio"], samplerate=speech["sampling_rate"])
    
    # Devuelve la respuesta en formato JSON.
    return jsonify({"text": reply, "audio": nombre_fichero})

@bp.route('/app/wav/<path:filename>')
def serve_wav(filename):
    return send_from_directory('/app/wav/', filename)

# Verifica si el script se ejecuta como programa principal y no como módulo importado.
if __name__ == "__main__":
    # Ejecuta la aplicación Flask en modo de depuración.
    bp.run(debug=True)