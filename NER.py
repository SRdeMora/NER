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

@app.route("/procesar", methods=["POST"])
def procesar_texto():
    datos = request.json
    texto = datos.get("texto", "")

    doc = nlp(texto)
    resultado = {"Empresa": "", "Dirección": "", "Ciudad": "", "Correo Electrónico": "", "Teléfono": ""}

    # Buscar correos electrónicos, números de teléfono y direcciones con regex
    correos = re.findall(patron_email, texto)
    telefonos = re.findall(patron_telefono, texto)
    direcciones = re.findall(patron_direccion, texto)

    for ent in doc.ents:
        if ent.label_ == "ORG":  # Empresas
            resultado["Empresa"] = ent.text
        elif ent.label_ in ["LOC", "FAC"]:  # Direcciones o ubicaciones
            if any(word in ent.text.lower() for word in ["calle", "avenida", "plaza"]):  
                resultado["Dirección"] = ent.text  # Guarda solo direcciones con nombres de calles
            elif resultado["Ciudad"] == "":  # Guarda la ciudad si aún no ha sido asignada
                resultado["Ciudad"] = ent.text  

    # Asociar correos electrónicos y teléfonos
    resultado["Correo Electrónico"] = ", ".join(correos) if correos else "-"
    resultado["Teléfono"] = ", ".join(telefonos) if telefonos else "-"

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
