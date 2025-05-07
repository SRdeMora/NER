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

# Expresión regular para números de teléfono
patron_telefono = r"\+?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}"

# Expresión regular para direcciones con nombres de calles y números
patron_direccion = r"\b(?:calle|avenida|av\.|c\.|cll\.|carrera|cra\.|cr\.|pasaje|psje\.|boulevard|blvd\.|plaza|plz\.)\s+\D*?\s?\d+\b"

# Variable para almacenar el último resultado
ultimo_resultado = []

@app.route("/procesar", methods=["POST"])
def procesar_texto():
    global ultimo_resultado  # Guardar el último resultado

    datos = request.json
    texto = datos.get("texto", "")

    doc = nlp(texto)
    resultado = []

    # Buscar correos electrónicos y números de teléfono antes de analizar entidades
    correos = re.findall(patron_email, texto)
    telefonos = re.findall(patron_telefono, texto)
    direcciones = re.findall(patron_direccion, texto)

    for ent in doc.ents:
        if ent.label_ == "ORG":  # Empresas
            resultado.append({"Empresa": ent.text, "Dirección": "", "Número": "", "Correo Electrónico": "", "Nombre": "", "Teléfono": ""})
        elif ent.label_ == "PERSON":  # Nombres de personas
            if resultado:
                resultado[-1]["Nombre"] = ent.text

    # Agregar direcciones extraídas por regex
    if direcciones and resultado:
        resultado[-1]["Dirección"] = ", ".join(direcciones)

    # Agregar correos electrónicos
    if correos and resultado:
        resultado[-1]["Correo Electrónico"] = ", ".join(correos)  

    # Agregar números de teléfono
    if telefonos and resultado:
        resultado[-1]["Teléfono"] = ", ".join(telefonos)

    ultimo_resultado = resultado  # Guardar resultado para futuras consultas
    return jsonify(resultado)

@app.route("/ultimo", methods=["GET"])
def obtener_ultimo():
    return jsonify(ultimo_resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
