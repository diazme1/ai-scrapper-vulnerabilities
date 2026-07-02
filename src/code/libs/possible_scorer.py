import json

# Tu matriz de riesgo definida como un diccionario
MATRIZ_SCORING = {
    "email_expuesto": 8,
    "telefono_expuesto": 10,
    "mfa_desactivada": 20,
    "contrasena_filtrada": 30,
    "contrasena_reutilizada": 25,
    "contrasenas_guardadas_en_navegador": 15,
    "contrasenas_guardadas_en_doc_digital": 25,
    "redes_sociales_publicas": 15,
    "conexion_frecuente_a_redes_publicas": 10,
    "datos_personales_expuestos": 15,
    "antivirus_desactivado": 15,
    "compras_online_frecuentes": 10,
    "backup_inexistente": 18
}

# class ScrapperHTML:

#     def __init__(self, config_path: str):

#         with open(Path(config_path), "r", encoding="utf-8") as file:
#             config = yaml.safe_load(file)

#         self.scores = config["scores"]
#         self.levels = config["levels"]


def calcular_nivel_riesgo(score_total):
    """Clasifica el riesgo total en niveles para facilitar la lectura."""
    if score_total < 30:
        return "Bajo"
    elif score_total < 70:
        return "Medio"
    elif score_total < 120:
        return "Alto"
    else:
        return "Crítico"

def evaluar_perfil(datos_scraper, info_interna_usuario):
    """
    Cruza los datos extraídos de la web con la información interna del sistema 
    para calcular el nivel de vulnerabilidad de un perfil.
    """
    score_final = 0
    factores_de_riesgo = []

    # 1. Mapear los resultados del Scraper a la Matriz
    if len(datos_scraper.get("emails_encontrados", [])) > 0:
        score_final += MATRIZ_SCORING["email_expuesto"]
        factores_de_riesgo.append("email_expuesto")

    if len(datos_scraper.get("telefonos_encontrados", [])) > 0:
        score_final += MATRIZ_SCORING["telefono_expuesto"]
        factores_de_riesgo.append("telefono_expuesto")

    # Si encontramos nombres o direcciones de empresas, consideramos exposición personal
    nombres = datos_scraper.get("nombres_detectados", [])
    lugares = datos_scraper.get("lugares_o_empresas", [])
    if len(nombres) > 0 or len(lugares) > 0:
        score_final += MATRIZ_SCORING["datos_personales_expuestos"]
        factores_de_riesgo.append("datos_personales_expuestos")

    # 2. Sumar la información de infraestructura/hábitos (que viene de otro sistema)
    for clave, estado in info_interna_usuario.items():
        if estado is True and clave in MATRIZ_SCORING:
            score_final += MATRIZ_SCORING[clave]
            factores_de_riesgo.append(clave)

    return {
        "score_total": score_final,
        "nivel_riesgo": calcular_nivel_riesgo(score_final),
        "factores_detectados": factores_de_riesgo
    }

# === Simulación de Integración ===
if __name__ == "__main__":
    # Estos son los datos que escupió tu bot de BeautifulSoup/spaCy
    resultado_bot = {
        "emails_encontrados": ["juan.perez@empresa.com.ar"],
        "telefonos_encontrados": ["11-4321-8765"],
        "nombres_detectados": ["Juan Pérez", "María Laura Gómez"],
        "lugares_o_empresas": ["Av. Corrientes 1234"]
    }
    
    # Estos son los datos de hábitos o infraestructura de ese usuario particular 
    # (En un entorno real, esto se consultaría a la base de datos)
    contexto_usuario = {
        "mfa_desactivada": True,
        "backup_inexistente": True,
        "contrasena_filtrada": False, 
        "antivirus_desactivado": False
    }

    reporte_vulnerabilidad = evaluar_perfil(resultado_bot, contexto_usuario)
    
    print(json.dumps(reporte_vulnerabilidad, indent=4, ensure_ascii=False))