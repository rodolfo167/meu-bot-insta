from flask import Flask, request
import requests
import google.generativeai as genai
import os

app = Flask(__name__)

# --- CONFIGURATIONS ---
VERIFY_TOKEN = "rodolfo123superseguro"
# Your Long-Lived Token from Facebook
PAGE_ACCESS_TOKEN = "EAAWtJy3WmlsBQhsKz8RJdhZBsSEkdyT8vmSnK639lhJNe3P5e4jBkwd0q7RVSCmVWEjDlJtplczFG9pcvTGyZCFtoFO6XekDzE66RDHidvJOwqnv4q8PPOvyWwpZAPZB1LrEcX7VbWOXr1duXeykO4FCRRFbFZCPqYxvZA5vSMMt0XJTbfm7FIvWRk6kH6"
# Your Google Gemini API Key
GEMINI_API_KEY = "AIzaSyCi9HxWEIHXSzcdYm0_vCke-kGy8UDDUYI"

# Configure Google AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_ai_response(user_message):
    try:
        prompt = f"""
        Você é a Lara, especialista em vendas da Loja do Rodolfo.
        Sua missão é ser simpática e convencer o cliente a comprar.
        Informações importantes:
        - Estamos com 15% de desconto hoje usando o cupom RODOLFO15.
        - Aceitamos Pix e Cartão.
        - Se o cliente perguntar algo que você não sabe, peça para ele aguardar um humano.
        
        Pergunta do cliente: {user_message}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "Ops, tive um probleminha técnico. Pode repetir?"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Wrong token", 403

    elif request.method == 'POST':
        data = request.json
        if 'entry' in data:
            for entry in data['entry']:
                if 'messaging' in entry:
                    for msg in entry['messaging']:
                        # Check if it's a new text message from user
                        if 'message' in msg and 'text' in msg['message'] and 'is_echo' not in msg['message']:
                            sender_id = msg['sender']['id']
                            user_text = msg['message']['text']
                            
                            print(f"Message received: {user_text}")

                            # Get AI response
                            ai_answer = get_ai_response(user_text)

                            # Send back to Instagram
                            url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                            payload = {
                                "recipient": {"id": sender_id},
                                "message": {"text": ai_answer}
                            }
                            fb_response = requests.post(url, json=payload)
                            print(f"DEBUG FACEBOOK: {fb_response.status_code} - {fb_response.text}")

        return "OK", 200

if __name__ == '__main__':
    # Running on port 3000 as configured for Render
    app.run(host='0.0.0.0', port=3000)
