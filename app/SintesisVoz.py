from transformers import pipeline
from datasets import load_dataset # Puede entrar en conflicto con otro módulo datasets de TensorFlow.
import soundfile as sf
import torch
import io

# Este primer bloque iría en app.py fuera de los renders de las páginas o en su fichero py independiente.

# Modelo descargado por pipeline
synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")
# Datasets de voces
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
# Índice del embedding de voz utilizado
voz = 5000
# Voz embedding a tensor
speaker_embedding = torch.tensor(embeddings_dataset[voz]["xvector"]).unsqueeze(0)
# Conversión

# Este bloque es solo para pruebas. El texto a generar lo recibirá del chatbot.
# Si la generación falla directamente no generaría voz. Lo manejaría de otra manera.

# Entrada de texto. 
texto = input("TEXTO A GENERAR: ")
# Texto por defecto
texto_defecto = "Input text not found, generating error message."
if texto == "":
    texto = texto_defecto

# Este bloque irá después de la generación de texto del chatbot, seguramente en un bloque
# app.route("/ruta/a/la/pagina", methods=["GET", "POST"])
# def.pagina():
    # if request.method == "POST":
        # <Transcripción audio>
        # <Generación chatbot>
        # <Síntesis de voz, este bloque>

# Conversión
speech = synthesiser(texto, forward_params={"speaker_embeddings": speaker_embedding})
# Convertir el audio a un buffer de bytes por si no queremos generar ficheros de audio permanentes.
buffer = io.BytesIO()
sf.write(buffer, speech["audio"], samplerate=speech["sampling_rate"], format='WAV')
buffer.seek(0)  # Regresar al inicio del buffer para la lectura
# Guardado fichero por si queremos guardarlos de forma permanente.
sf.write(f"app/wav/{voz}-{texto}.wav", speech["audio"], samplerate=speech["sampling_rate"])
# Respuesta a la petición POST
        # return Response(buffer, mimetype="audio/wav")
    # return render_template("/ruta/a/la/pagina/pagina.html")

# Mensaje debug
print(f"Fichero {voz}-{texto}.wav generado")