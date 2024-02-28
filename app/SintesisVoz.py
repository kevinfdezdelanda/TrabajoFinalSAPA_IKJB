from transformers import pipeline
from datasets import load_dataset # Puede entrar en conflicto con otro módulo datasets de TensorFlow.
import soundfile as sf
import torch

# Índice del embedding de voz utilizado
voz = 27

# Texto por defecto
texto_defecto = """Text to speech failed. Try again"""

# Modelo descargado por pipeline
synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts")

# Datasets de voces
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

# Entrada de texto. 
texto = input("TEXTO A GENERAR: ")

# Fallo en el texto 
if texto == "":
    print("TEXTO NO INTRODUCIDO, UTILIZANDO EL TEXTO POR DEFECTO:")
    texto = texto_defecto
    print(texto)
    
# Voz embedding a tensor
speaker_embedding = torch.tensor(embeddings_dataset[voz]["xvector"]).unsqueeze(0)

# Conversión
speech = synthesiser(texto, forward_params={"speaker_embeddings": speaker_embedding})

# Guardado fichero
sf.write(f"wav/Voz-{voz}.Texto-{texto}.wav", speech["audio"], samplerate=speech["sampling_rate"])

# Mensaje
print(f"Fichero Voz-{voz}.Texto-{texto}.wav generado")
