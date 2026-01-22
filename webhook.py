from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "rodolfo123superseguro"  # Mude pra o token que você inventou no Meta!

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verificação do Meta
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            print("Verificação OK! Respondendo challenge.")
            return request.args.get('hub.challenge')
        else:
            return "Token errado", 403
    elif request.method == 'POST':
        print("Mensagem recebida do Instagram:", request.json)
        return "OK", 200

if __name__ == '__main__':
    app.run(port=3000)