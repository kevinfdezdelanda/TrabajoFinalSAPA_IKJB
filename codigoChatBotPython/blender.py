# pip install transformers torch
# Antes de utilizar este scipt tenemos que ejecutar el comando de arriba en bash 
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration

# Inicializar el modelo y el tokenizador
model_name = 'facebook/blenderbot-400M-distill'
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

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

# Función para generar respuestas
def generate_response(user_input):
    for keyword in prohibited_keywords:
        if keyword in user_input.lower():
            return "Im sorry, but i prefer to not talk about these topics "
    
    # Tokenizar la entrada del usuario
    inputs = tokenizer([user_input], return_tensors='pt')

    # Generar una respuesta
    result = model.generate(**inputs, max_length=40)

    # Decodificar y mostrar la respuesta
    reply = tokenizer.decode(result[0], skip_special_tokens=True)
    return reply

# Bucle para mantener la conversación
print("BlenderBot: Hi! How can I help you today? (Type 'exit' to end the conversation.)")
while True:
    # Leer la entrada del usuario
    user_input = input("You: ") #Preguntas no muy especificas, sobre africa no sabe responder nada
    if user_input.lower().strip() == 'exit':
        break
    # Generar y mostrar la respuesta
    response = generate_response(user_input)
    print(f"BlenderBot: {response}")