import re
import spacy
from bs4 import BeautifulSoup
import requests
import json

# Cargamos el modelo de lenguaje en español de spaCy
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Error: Falta el modelo de spaCy. Ejecutá: python -m spacy download es_core_news_sm")
    exit()

def limpiar_html(html):
    """Extrae únicamente el texto visible del HTML, eliminando scripts y estilos."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Eliminamos etiquetas que no contienen texto útil
    for script in soup(["script", "style", "noscript", "header", "footer"]):
        script.extract()
        
    texto = soup.get_text(separator=' ')
    
    # Limpiamos espacios en blanco múltiples
    texto_limpio = re.sub(r'\s+', ' ', texto).strip()
    return texto_limpio

def extraer_datos_por_patron(texto):
    """Usa Expresiones Regulares para mails y teléfonos."""
    # Regex para emails
    patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(patron_email, texto)
    
    # Regex para teléfonos (Formato genérico / flexible para Arg e intl)
    # Busca cosas como: +54 9 11 1234-5678, 11-1234-5678, 1545678910
    patron_telefono = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}'
    telefonos = re.findall(patron_telefono, texto)
    
    # Limpiamos duplicados y falsos positivos cortos
    telefonos = [tel.strip() for tel in telefonos if len(tel.replace(" ", "").replace("-", "")) >= 8]
    
    return list(set(emails)), list(set(telefonos))

def extraer_entidades_nlp(texto):
    """Usa Inteligencia Artificial (spaCy) para entender nombres y lugares."""
    doc = nlp(texto)
    
    nombres = []
    direcciones_lugares = []
    
    for entidad in doc.ents:
        if entidad.label_ == "PER": # PER = Person (Persona)
            nombres.append(entidad.text)
        elif entidad.label_ in ["LOC", "ORG"]: # LOC = Location, ORG = Organization
            direcciones_lugares.append(entidad.text)
            
    return list(set(nombres)), list(set(direcciones_lugares))

def escanear_web(url_o_html, es_url=True):
    """Función principal que orquesta todo el proceso."""
    if es_url:
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url_o_html, headers=headers)
            response.raise_for_status()
            html_crudo = response.text
        except Exception as e:
            return {"error": str(e)}
    else:
        try:
            with open(url_o_html, 'r', encoding='utf-8') as archivo:
                html_crudo = archivo.read()
        except FileNotFoundError:
            return {"error": f"El archivo especificado no existe: {url_o_html}"}
        except Exception as e:
            return {"error": f"Error al leer el archivo: {str(e)}"}

    # 1. Extraer solo el texto legible
    texto_puro = limpiar_html(html_crudo)
    
    # 2. Extraer datos estructurados (Regex)
    emails, telefonos = extraer_datos_por_patron(texto_puro)
    
    # 3. Extraer entidades abstractas (NLP)
    nombres, lugares = extraer_entidades_nlp(texto_puro)
    
    return {
        "emails_encontrados": emails,
        "telefonos_encontrados": telefonos,
        "nombres_detectados": nombres,
        "lugares_o_empresas": lugares
    }

# === Ejecución Principal ===
if __name__ == "__main__":
    # Simulamos un HTML desordenado y sin clases útiles
    html_prueba_1 = "data/instagram.html"

    url = "https://www.infobae.com"
    
    resultados = escanear_web(html_prueba_1, es_url=False)
    print(json.dumps(resultados, indent=4, ensure_ascii=False))