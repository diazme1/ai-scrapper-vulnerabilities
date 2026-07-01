import re
import spacy
from bs4 import BeautifulSoup
import requests
import json

# Cargamos el modelo de lenguaje en español de spaCy
# (Nota: Te sugiero fuertemente usar "es_core_news_lg" para evitar falsos positivos en nombres)
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Error: Falta el modelo de spaCy. Ejecutá: python -m spacy download es_core_news_lg")
    exit()

def extraer_datos_por_patron(texto):
    """Usa Expresiones Regulares para extraer emails, teléfonos, usuarios y fechas del texto."""
    # Regex para emails y teléfonos (los que ya tenías)
    patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(patron_email, texto)
    
    patron_telefono = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}'
    telefonos = re.findall(patron_telefono, texto)
    telefonos = [tel.strip() for tel in telefonos if len(tel.replace(" ", "").replace("-", "")) >= 8]
    
    # NUEVO: Regex para nombres de usuario (atrapa @usuario, @nombre.apellido, @dev_99)
    patron_usuario = r'(?<![\w.-])@[\w.]+'
    usuarios = re.findall(patron_usuario, texto)
    
    # NUEVO: Regex para fechas (atrapa tanto "2023-08-15" como "2026-06-30 09:18:42 UTC-3")
    patron_fecha = r'\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2}\s*UTC[-+]\d+)?'
    fechas = re.findall(patron_fecha, texto)
    
    return list(set(emails)), list(set(telefonos)), list(set(usuarios)), list(set(fechas))

def extraer_entidades_nlp(texto):
    """Usa Inteligencia Artificial (spaCy) para entender nombres y lugares en el texto."""
    doc = nlp(texto)
    nombres = []
    direcciones_lugares = []
    
    for entidad in doc.ents:
        if entidad.label_ == "PER":
            nombres.append(entidad.text)
        elif entidad.label_ in ["LOC"]:
            texto_entidad = entidad.text
            
            es_email_o_web = "@" in texto_entidad or re.search(r'\.[a-zA-Z]{2,4}\b', texto_entidad)
            
            if not es_email_o_web:
                direcciones_lugares.append(texto_entidad)
            
    return list(set(nombres)), list(set(direcciones_lugares))

def escanear_web(url_o_html, es_url=True):
    """Orquesta el proceso leyendo contenedores lógicos de arriba hacia abajo (Top-Down)."""
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

    soup = BeautifulSoup(html_crudo, 'html.parser')
    
    # 1. Limpiamos scripts y código oculto que no queremos procesar
    for script in soup(["script", "style", "noscript"]):
        script.extract()
        
    personas_encontradas = []
    
    # Memorias para evitar duplicar procesamientos de hijos si el padre ya se leyó
    emails_ya_vistos = set()
    nombres_ya_vistos = set()
    usuarios_ya_vistos = set()
    
    # Sumamos palabras que usa este HTML específico para etiquetar datos
    palabras_basura = [
        "Usuario", "Correo", "Ubicación", "Teléfono", "Tel", "Celular", "Mail", "Publicado", 
        "Argentina", "Contacto", "Nombre", "Fecha", "registro", "Aviso", "Importante", 
        "Seguridad", "Estimado", "React", "WhatsApp", "Rol", "Administrador", "Base de Datos", 
        "Moderadora", "Contenido", "corporativo", "guardias"
    ]     
    # 2. Iteramos sobre los contenedores lógicos más comunes en maquetación
    for bloque in soup.find_all(['article', 'section', 'div', 'li']):
        
        # TRUCO CLAVE: Juntamos todo el texto del contenedor con un espacio.
        # Esto evita separar a Emilia de su correo que está en el <p> de abajo.
        texto_bloque = bloque.get_text(separator=' ', strip=True)
        
        if len(texto_bloque) < 10:
            continue
            
        emails, telefonos, usuarios, fechas = extraer_datos_por_patron(texto_bloque)
        nombres_crudos, lugares = extraer_entidades_nlp(texto_bloque)
        
        # Limpieza de nombres
        nombres_limpios = []
        for nombre in nombres_crudos:
            nombre_temp = nombre
            for basura in palabras_basura:
                # Borramos la basura usando regex para ignorar mayúsculas/minúsculas
                nombre_temp = re.sub(rf'\b{basura}\b', '', nombre_temp, flags=re.IGNORECASE)
            
            nombre_temp = nombre_temp.strip()
            
            # Solo aceptamos el nombre si le quedó Nombre + Apellido
            if len(nombre_temp.split()) > 1:
                nombres_limpios.append(nombre_temp)
        

        lista_negra_lugares = {
            "ubicación", "ubicacion", "telefono", "teléfono", "tel", "mail", "correo", 
            "usuario", "fecha", "registro", "contacto", "administrador", "moderadora", 
            "empresa", "whatsapp", "react", "código", "rol", "contenido", "corporativo"
        }

        lugares_limpios = []
        for lugar in lugares:
            lugar_temp = lugar
            
            # PASO 1: Quitamos las palabras basura específicas (si están dentro de la frase)
            for basura in palabras_basura:
                lugar_temp = re.sub(rf'\b{basura}\b', '', lugar_temp, flags=re.IGNORECASE)
            
            # PASO 2: Limpiamos signos, comas y espacios extra
            lugar_clean = re.sub(r'^[,\s:\-]+|[,\s:\-]+$', '', lugar_temp).strip()
            
            if lugar_clean.lower() not in lista_negra_lugares and len(lugar_clean) > 3:
                lugares_limpios.append(lugar_clean)

        # 3. FILTRO DE DENSIDAD
        # Lo ignoramos y dejamos que el bucle siga iterando hacia sus hijos más pequeños.
        if len(set(nombres_limpios)) >= 2 or len(emails) >= 3:
            continue
            
        nuevos_emails = [e for e in emails if e not in emails_ya_vistos]
        nuevos_nombres = [n for n in nombres_limpios if n not in nombres_ya_vistos]
        nuevos_usuarios = [u for u in usuarios if u not in usuarios_ya_vistos]
        
        if nuevos_emails or nuevos_nombres or nuevos_usuarios:
            nombre_final = nuevos_nombres[0] if nuevos_nombres else (nombres_limpios[0] if nombres_limpios else "Desconocido")
            
            perfil = {
                "nombre": nombre_final,
                "usuarios": nuevos_usuarios, 
                "emails": nuevos_emails,
                "telefonos": telefonos,
                "ubicaciones": lugares_limpios,
                "fechas": fechas   
            }
            personas_encontradas.append(perfil)
            
            # Actualizamos la memoria
            emails_ya_vistos.update(emails)
            nombres_ya_vistos.update(nombres_limpios)
            usuarios_ya_vistos.update(usuarios)

    return {
        "estado": "completado",
        "total_personas_encontradas": len(personas_encontradas),
        "personas": personas_encontradas
    }

# === Ejecución Principal ===
if __name__ == "__main__":
    # Apuntamos a tu archivo local
    html_prueba_1 = "data/instagram.html"
    html_prueba_2 = "data/instagram2.html"
    
    # Ejecutamos el scraper
    resultados = escanear_web(html_prueba_2, es_url=False)
    
    print(json.dumps(resultados, indent=4, ensure_ascii=False))