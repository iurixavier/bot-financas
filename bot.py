from flask import Flask, request
from datetime import datetime, timedelta
import csv
import os

app = Flask(__name__)

CATEGORIAS = {
    "farmácia": "Saúde",
    "remédio": "Saúde",
    "hospital": "Saúde",
    "cerveja": "Lazer",
    "cinema": "Lazer",
    "bar": "Lazer",
    "mercado": "Alimentação",
    "supermercado": "Alimentação",
    "comida": "Alimentação",
    "gasolina": "Transporte",
    "uber": "Transporte",
    "ônibus": "Transporte",
    "livro": "Educação"
}

CSV_FILE = "gastos.csv"

def salvar_gasto(valor, descricao, categoria):
    data = datetime.now().strftime("%Y-%m-%d")
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data, valor, categoria, descricao])

def ler_gastos():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        return list(reader)

def categorizar(descricao):
    descricao = descricao.lower()
    for palavra, categoria in CATEGORIAS.items():
        if palavra in descricao:
            return categoria
    return "Outros"

def resumo_periodo(dias):
    hoje = datetime.now()
    gastos = ler_gastos()
    total_por_categoria = {}
    for linha in gastos:
        data_str, valor, categoria, _ = linha
        data = datetime.strptime(data_str, "%Y-%m-%d")
        if hoje - data <= timedelta(days=dias):
            valor = float(valor)
            total_por_categoria[categoria] = total_por_categoria.get(categoria, 0) + valor
    return total_por_categoria

@app.route("/mensagem", methods=["POST"])
def mensagem():
    texto = request.form.get("Body", "").lower()
    resposta = "Não entendi. Envie algo como: 'Gastei 10 mercado'."

    if texto.startswith("gastei"):
        partes = texto.split()
        try:
            valor = float(partes[1])
            descricao = " ".join(partes[2:])
            categoria = categorizar(descricao)
            salvar_gasto(valor, descricao, categoria)
            resposta = f"Anotado: R$ {valor:.2f} em '{descricao}' (categoria: {categoria})."
        except:
            resposta = "Formato inválido. Use: Gastei 10 mercado"

    elif "resumo da semana" in texto:
        resumo = resumo_periodo(7)
        if resumo:
            resposta = "📊 *Resumo da semana:*\n" + "\n".join(
                [f"{cat}: R$ {val:.2f}" for cat, val in resumo.items()])
        else:
            resposta = "Nenhum gasto registrado nesta semana."

    elif "resumo do mês" in texto:
        resumo = resumo_periodo(30)
        if resumo:
            resposta = "📊 *Resumo do mês:*\n" + "\n".join(
                [f"{cat}: R$ {val:.2f}" for cat, val in resumo.items()])
        else:
            resposta = "Nenhum gasto registrado neste mês."

    elif "total" in texto:
        gastos = ler_gastos()
        total = sum(float(l[1]) for l in gastos)
        resposta = f"💰 Total registrado: R$ {total:.2f}"

    elif "resetar" in texto:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        resposta = "Todos os registros foram apagados."

    return f"<Response><Message>{resposta}</Message></Response>"
if __name__ == "__main__":
    app.run(debug=True)

