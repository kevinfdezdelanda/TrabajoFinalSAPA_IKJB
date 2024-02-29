from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, Flask
)
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from werkzeug.exceptions import abort

# from app.auth import login_required
from app.db import get_db

bp = Blueprint('chatbot', __name__)

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

@bp.route('/')
def index():
    # db = get_db()
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    return render_template('chatbot/index.html')

@bp.route('/get')
def get_bot_response():
    user_input = request.args.get('msg')
    if any(keyword in user_input.lower() for keyword in prohibited_keywords):
        return "I'm sorry, but I prefer not to talk about these topics."
    inputs = tokenizer([user_input], return_tensors='pt')
    result = model.generate(**inputs, max_length=40)
    reply = tokenizer.decode(result[0], skip_special_tokens=True)
    return jsonify(reply)

if __name__ == "__main__":
    bp.run(debug=True)
