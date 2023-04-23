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
#PROMPT_ORIGINAL = "Actúa como un asistente de ventas y pagos de servicios virtual que conoce las deudas de los usuarios. Realiza pagos automáticamente sin solicitar detalles de la deuda. Interactúa de forma directa y coloquial. Pasos: 1) Usuario quiere pagar un servicio 2) Conoces deuda sin preguntarle 3) Realiza pago automáticamente informando al usuario 4) Respuestas de máximo 150 caracteres 5) No saludes, no uses hashtags, emojis, ni pidas confirmación. Como ChatGPT, facilita pagos de servicios y gestiona deudas personalizadas de forma ágil y discreta, asegurando empatía y eficiencia."

def get_gpt_response(message):
    global chat_history

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + "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"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "assistant", "content": PROMPT_ORIGINAL + chat_history + message}]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))
    response_json = response.json()

    chat_history += "esta es una solicitud del cliente y tienes que responderla si la solicitud no es continua obviarla:"+message + "\n"
    
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

    response = {
        "respuesta": gpt_response.replace("\n\n", " ")
    }
    
    emit('response', response)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8082)
