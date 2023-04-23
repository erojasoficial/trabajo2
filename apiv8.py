from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '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'
socketio = SocketIO(app, cors_allowed_origins='*')
CORS(app)

chat_history = ""
PROMPT_ORIGINAL = "Actúa como Yanapaq, un asistente virtual altamente eficiente en pagos de servicios, que conoce las deudas de los usuarios y realiza pagos sin requerir información adicional. Interactúa de manera directa y coloquial, con empatía y rapidez. Pasos: 1) Usuario solicita pagar un servicio 2) Yanapaq detecta deuda automáticamente 3) Procesa pago directamente sin solicitar detalles y comunica al usuario 4) Respuestas concisas (max 150 caracteres) 5) Evita saludos, hashtags, emojis y confirmaciones. Yanapaq se ajusta al contexto, gestionando múltiples tareas de manera eficiente y habilidosa, efectuando pagos de diversos servicios sin solicitar ningún dato adicional."

def check_and_reset_chat_history():
    global chat_history

    check_payment_success_message = "¿Indica la respuesta anterior un pago exitoso?"
    success_response = get_gpt_response(check_payment_success_message)

    if "sí" in success_response.lower() or "si" in success_response.lower():
        chat_history = ""
        return True
    else:
        return False

def get_gpt_response(message):
    global chat_history

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + "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"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "assistant", "content": PROMPT_ORIGINAL + chat_history + message}],    
        "temperature": 0.4
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
    response_json = response.json()

    chat_history += ""+message + "\n"
    
    if response_json.get('choices'):
        return response_json['choices'][0]['message']['content']
    else:
        return "No se pudo obtener una respuesta del modelo GPT."

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    global chat_history

    message = data['message']
    gpt_response = get_gpt_response(message)

    if check_and_reset_chat_history():
        response = {
            "respuesta": gpt_response.replace("\n\n", " ")
        }
    else:
        response = {
            "respuesta": gpt_response.replace("\n\n", " ")
        }
    
    emit('response', response)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8082)
