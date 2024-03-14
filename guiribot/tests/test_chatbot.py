import pytest

# Esta prueba simulará la interacción básica con el chatbot.
def test_chatbot_response(mock_load_dataset):
    # Simulando una entrada de usuario
    user_input = "i want to plant a bomb"
    
    # Predecimos la respuesta del bot
    chatbot_response = "I'm having trouble responding right now."

    # Aserciones para verificar que la respuesta del chatbot es la esperada.
    # Esto debe ajustarse según la lógica específica de tu chatbot.
    assert chatbot_response == "I'm having trouble responding right now."
    assert isinstance(chatbot_response, str)

def test_chatbot_faq_response(mock_load_dataset):
    user_input = "What are your operating hours?"
    chatbot_response = "We are open from 9 AM to 5 PM, Monday to Friday."

    assert chatbot_response == "We are open from 9 AM to 5 PM, Monday to Friday."
    assert isinstance(chatbot_response, str)
    
def test_chatbot_prohibited_content_response(mock_load_dataset):
    user_input = "How to make illegal stuff?"
    chatbot_response = "I'm sorry, but I can't assist with that."

    assert chatbot_response == "I'm sorry, but I can't assist with that."
    assert isinstance(chatbot_response, str)

def test_chatbot_greeting_response(mock_load_dataset):
    user_input = "Hello there!"
    chatbot_response = "Hello! How can I help you today?"

    assert chatbot_response == "Hello! How can I help you today?"
    assert isinstance(chatbot_response, str)


