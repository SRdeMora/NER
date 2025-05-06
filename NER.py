from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import re

app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

# Cargar modelo de spaCy en español
nlp = spacy.load("es_core_news_md")

# Expresión regular para correos electrónicos
patron_email = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Variable para almacenar el último resultado
ultimo_resultado = []

@app.route("/procesar", methods=["POST"])
def procesar_texto():
    global ultimo_resultado  # Guardar el último resultado

    datos = request.json
    texto = datos.get("texto", "")

    doc = nlp(texto)
    resultado = []

    for ent in doc.ents:
        if ent.label_ == "ORG":  # Empresas
            resultado.append({"Empresa": ent.text, "Dirección": "", "Correo Electrónico": "", "Nombre": ""})
        elif ent.label_ in ["LOC", "FAC"]:  # Ubicaciones y direcciones
            if resultado:
                resultado[-1]["Dirección"] = ent.text
        elif ent.label_ == "PERSON":  # Nombres de personas
            if resultado:
                resultado[-1]["Nombre"] = ent.text
        elif re.match(patron_email, ent.text):  # Correos electrónicos
            if resultado:
                resultado[-1]["Correo Electrónico"] = ent.text

    ultimo_resultado = resultado  # Guardar resultado para futuras consultas
    return jsonify(resultado)

@app.route("/ultimo", methods=["GET"])
def obtener_ultimo():
    return jsonify(ultimo_resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
