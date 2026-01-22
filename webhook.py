from flask import Flask, request
import requests
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIGURAÇÕES ---
VERIFY_TOKEN = "rodolfo123superseguro"
# Seu token longo do Facebook (EAA...)
PAGE_ACCESS_TOKEN = "EAAWtJy3WmlsBQhsKz8RJdhZBsSEkdyT8vmSnK639lhJNe3P5e4jBkwd0q7RVSCmVWEjDlJtplczFG9pcvTGyZCFtoFO6XekDzE66RDHidvJOwqnv4q8PPOvyWwpZAPZB1LrEcX7VbWOXr1duXeykO4FCRRFbFZCPqYxvZA5vSMMt0XJTbfm7FIvWRk6kH6"
# Sua chave do Google Gemini
GEMINI_API_KEY = "AIzaSyCi9HxWEIHXSzcdYm0_vCke-kGy8UDDUYI"

# Configura a IA do Google
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def buscar_resposta_ia(mensagem_usuario):
    try:
        # Prompt de personalidade para a Lara
        prompt = f"""
        Você é a Lara, especialista em vendas da Loja do Rodolfo.
        Sua missão é ser simpática e convencer o cliente a comprar.
        Informações importantes:
        - Estamos com 15% de desconto hoje usando o cupom RODOLFO15.
        - Nosso catálogo está no link: [COLOQUE SEU LINK AQUI].
        - Aceitamos Pix e Cartão.
        - Se o cliente perguntar algo que você não sabe, peça para ele aguardar um humano.
        
        Pergunta do cliente: {mensagem_usuario}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Ops, tive um probleminha técnico. Pode repetir?"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return "Token errado", 403

    elif request.method == 'POST':
        data = request.json
        
        if 'entry' in data:
            for entry in data['entry']:
                if 'messaging' in entry:
                    for msg in entry['messaging']:
                        # FILTRO IMPORTANTE: Só processa se for texto novo do usuário
                        if 'message' in msg and 'text' in msg['message'] and 'is_echo' not in msg['message']:
                            
                            sender_id = msg['sender']['id']
                            user_text = msg['message']['text']
                            
                            print(f"\n--- Mensagem de {sender_id}: {user_text} ---")

                            # 1. Chama o Gemini para gerar a resposta
                            resposta_ia = buscar_resposta_ia(user_text)

                            # 2. Configura o envio para a API do Facebook/Instagram
                            url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
                            payload = {
                                "recipient": {"id": sender_id},
                                "message": {"text": resposta_ia}
                            }
                            
                            # 3. Faz o envio real
                            fb_response = requests.post(url, json=payload)
                            
                            # 4. Mostra o resultado do envio no terminal (Crucial para testes)
                            print(f"DEBUG FACEBOOK: {fb_response.status_code} - {fb_response.text}")

        return "OK", 200

if __name__ == '__main__':
    # Roda o servidor na porta 3000
    app.run(port=3000)
