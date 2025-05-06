from flask import Flask, request, jsonify
import spacy
import re

app = Flask(__name__)

# Cargar el modelo de spaCy en español
nlp = spacy.load("es_core_news_md")

# Expresión regular para correos electrónicos
patron_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

@app.route("/procesar", methods=["POST"])
def procesar_texto():
    datos = request.json
    texto = datos.get("texto", "")

    doc = nlp(texto)
    resultado = []

    for ent in doc.ents:
        if ent.label_ == "ORG":
            resultado.append({"Empresa": ent.text, "Dirección": "", "Correo Electrónico": ""})
        elif ent.label_ == "LOC":
            if resultado:
                resultado[-1]["Dirección"] = ent.text
        elif re.match(patron_email, ent.text):
            if resultado:
                resultado[-1]["Correo Electrónico"] = ent.text

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
