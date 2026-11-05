from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# SEGURO - Pega das variáveis da Vercel, não fica no código
TOKEN = os.environ.get("TOKEN")
PHONE_ID = os.environ.get("PHONE_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "barril123")

CARDAPIO = {
    "11": ("X-Burguer", 30.00), "12": ("X-Bacon", 32.00), "13": ("X-Eggy", 32.00),
    "14": ("X-Salada", 32.00), "15": ("X-Tudo", 36.00),
    "21": ("X-Frango", 32.00), "22": ("X-Frango Bacon", 34.00), "23": ("X-Frango Eggy", 34.00),
    "24": ("X-Frango Salada", 34.00), "25": ("X-Frango Tudo", 38.00),
    "31": ("X-Boiçucanga", 38.00), "32": ("X-Barril do Mar", 54.00), "33": ("X-Barril do Boi", 60.00),
    "41": ("Combo X-Bacon", 42.00), "42": ("Combo Casal", 85.00), "43": ("Combo Barril do Mar", 68.00),
    "44": ("Combo Trio Barril", 119.00), "45": ("Combo Família Barril", 179.90),
    "51": ("Adic. Hambúrguer", 3.00), "52": ("Adic. Frango", 3.00), "53": ("Adic. Queijo", 3.00),
    "54": ("Adic. Presunto", 3.00), "55": ("Adic. Ovo", 3.00), "56": ("Adic. Bacon", 3.00),
    "57": ("Adic. Cebola", 3.00), "58": ("Adic. Tomate", 3.00), "59": ("Adic. Linguiça", 3.00),
    "510": ("Catupiry", 5.00), "511": ("Ketchup", 0.50), "512": ("Maionese", 0.50), "513": ("Patê de Alho", 1.00),
    "61": ("Coca Lata", 8.00), "62": ("Coca Zero Lata", 8.00), "63": ("Coca 2L", 18.00),
    "64": ("Refrigerante 2L", 18.00),
    "66": ("Água", 6.00), "67": ("Água com Gás", 8.00),
    "71": ("Batata 200g", 18.00), "72": ("Batata 400g", 28.00),
    "73": ("Frango a Passarinho", 45.00), "74": ("Pururuca", 35.00),
    "81": ("Pastel Frango", 25.00), "82": ("Pastel Frango Catupiry", 28.00),
    "83": ("Pastel Carne", 25.00), "84": ("Pastel Carne Queijo", 28.00),
    "85": ("Pastel Queijo", 24.00), "86": ("Pastel Calabresa", 25.00), "87": ("Pastel Pizza", 30.00),
}

MENU_PRINCIPAL = """🍔 *BARRIL DO MAR* - Boiçucanga
Digite o número:
1 - Hambúrguer
2 - Lanches de Frango
3 - Especiais
4 - Combos
5 - Adicionais
6 - Bebidas
7 - Porções
8 - Pastéis
9 - 🛒 Ver pedido
0 - Atendente"""

MENUS = {
    "1": "🍔 HAMBÚRGUER:\n11 X-Burguer R$30\n12 X-Bacon R$32\n13 X-Eggy R$32\n14 X-Salada R$32\n15 X-Tudo R$36\n\n0 Menu | 9 Pedido",
    "2": "🍗 FRANGO:\n21 X-Frango R$32\n22 X-Frango Bacon R$34\n23 X-Frango Eggy R$34\n24 X-Frango Salada R$34\n25 X-Frango Tudo R$38\n\n0 Menu | 9 Pedido",
    "3": "⭐ ESPECIAIS:\n31 X-Boiçucanga R$38\n32 X-Barril do Mar R$54\n33 X-Barril do Boi R$60\n\n0 Menu | 9 Pedido",
    "4": "🔥 COMBOS:\n41 Combo X-Bacon R$42\n42 Combo Casal R$85\n43 Combo Barril do Mar R$68\n44 Combo Trio R$119\n45 Combo Família Barril R$179,90\n4x X-Tudo + 2x Batata 400g + Coca 2L\n\n0 Menu | 9 Pedido",
    "5": "➕ ADICIONAIS:\n51 Hambúrguer R$3 | 52 Frango R$3 | 53 Queijo R$3\n54 Presunto R$3 | 55 Ovo R$3 | 56 Bacon R$3\n57 Cebola R$3 | 58 Tomate R$3 | 59 Linguiça R$3\n510 Catupiry R$5 | 511 Ketchup R$0,50 | 512 Maionese R$0,50 | 513 Patê Alho R$1\n\n0 Menu | 9 Pedido",
    "6": "🥤 BEBIDAS:\n61 Coca Lata R$8\n62 Coca Zero Lata R$8\n63 Coca 2L R$18\n64 Refrigerante 2L R$18\n66 Água R$6\n67 Água com Gás R$8\n\n0 Menu | 9 Pedido",
    "7": "🍟 PORÇÕES:\n71 Batata 200g R$18\n72 Batata 400g R$28\n73 Frango a Passarinho R$45\n74 Pururuca R$35\n\n0 Menu | 9 Pedido",
    "8": "🥟 PASTÉIS:\n81 Frango R$25\n82 Frango Catupiry R$28\n83 Carne R$25\n84 Carne Queijo R$28\n85 Queijo R$24\n86 Calabresa R$25\n87 Pizza R$30\n\n0 Menu | 9 Pedido",
}

carrinhos = {}

def responder(msg, telefone):
    msg = msg.strip()
    if telefone not in carrinhos:
        carrinhos[telefone] = []
    carrinho = carrinhos[telefone]
    if msg == "0":
        return MENU_PRINCIPAL
    if msg in MENUS:
        return MENUS[msg]
    if msg in CARDAPIO:
        nome, preco = CARDAPIO[msg]
        carrinho.append((nome, preco))
        return f"✅ {nome} adicionado! R${preco:.2f}\n\nDigite 9 para ver o pedido ou 0 para voltar ao menu"
    if msg == "9":
        if not carrinho:
            return "🛒 Carrinho vazio.\n\n" + MENU_PRINCIPAL
        total = sum(p for _, p in carrinho)
        texto = "🛒 Seu pedido:\n"
        for nome, preco in carrinho:
            texto += f"- {nome} - R${preco:.2f}\n"
        texto += f"\nTotal: R${total:.2f}\n\nDigite 91 para finalizar\n92 Limpar | 0 Voltar"
        return texto
    if msg == "91":
        return "Como vai ser?\n911 - Entrega\n912 - Retirada"
    if msg == "911":
        return "Qual bairro?\n1 - Boiçucanga - Taxa R$8\n2 - Camburi - Taxa R$12\n3 - Maresias - Taxa R$20"
    if msg == "912":
        return "✅ Retirada no Barril do Mar!\n\nQual forma de pagamento?\n1 Pix\n2 Crédito\n3 Débito\n4 Dinheiro\n\nDepois me manda seu nome."
    if msg == "92":
        carrinho.clear()
        return "Carrinho limpo! ✅\n\n" + MENU_PRINCIPAL
    if msg.lower() in ["oi", "ola", "olá", "menu", "inicio", "início"]:
        return MENU_PRINCIPAL
    return "Opção inválida 😅\n\n" + MENU_PRINCIPAL

def enviar_whatsapp(telefone, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": telefone, "type": "text", "text": {"body": texto}}
    requests.post(url, headers=headers, json=data)

@app.route("/api/index", methods=["GET"])
def verificar():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erro", 403

@app.route("/api/index", methods=["POST"])
def receber():
    data = request.json
    try:
        msg_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
        telefone = msg_data["from"]
        texto = msg_data["text"]["body"]
        resposta = responder(texto, telefone)
        enviar_whatsapp(telefone, resposta)
    except:
        pass
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "Bot Barril do Mar online!"

if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", debug=True)