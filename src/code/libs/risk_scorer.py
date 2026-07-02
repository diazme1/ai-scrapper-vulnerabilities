import json
from datetime import datetime

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
    "backup_inexistente": 18,
    "riesgo_doxxing_agrupado": 25,
    "datos_recientes": 15,
    "datos_viejos": -15,
    "rol_expuesto": 50
}


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

def evaluar_perfil(perfil_scraper, info_interna_usuario):
    """
    Cruza los datos extraídos de un perfil específico con la información interna.
    Incluye lógica para detectar riesgo de Doxxing por agrupación de datos.
    """
    score_final = 0
    factores_de_riesgo = []
    
    # Contador de datos de un mismo perfil expuesto
    cant_datos_expuestos = 0

    # 1. Mapear los resultados del Scraper a la Matriz
    if len(perfil_scraper.get("emails", [])) > 0:
        score_final += MATRIZ_SCORING["email_expuesto"]
        factores_de_riesgo.append("email_expuesto")
        cant_datos_expuestos += 1

    if len(perfil_scraper.get("telefonos", [])) > 0:
        score_final += MATRIZ_SCORING["telefono_expuesto"]
        factores_de_riesgo.append("telefono_expuesto")
        cant_datos_expuestos += 1

    # Verificamos exposición de nombre o ubicación
    tiene_nombre = perfil_scraper.get("nombre") and perfil_scraper.get("nombre") != "Desconocido"
    tiene_ubicacion = len(perfil_scraper.get("ubicaciones", [])) > 0
    
    if tiene_nombre or tiene_ubicacion:
        score_final += MATRIZ_SCORING["datos_personales_expuestos"]
        factores_de_riesgo.append("datos_personales_expuestos")
        cant_datos_expuestos += 1


    if cant_datos_expuestos >= 3:
        score_final += MATRIZ_SCORING["riesgo_doxxing_agrupado"]
        factores_de_riesgo.append("riesgo_doxxing_agrupado")

    fechas = perfil_scraper.get("fechas", [])
    if fechas:
        fechas_datetime = []
        for f in fechas:
            try:
                # Tomamos solo los primeros 10 caracteres (YYYY-MM-DD)
                fecha_limpia = f[:10]
                fechas_datetime.append(datetime.strptime(fecha_limpia, "%Y-%m-%d"))
            except ValueError:
                continue # Ignoramos fechas mal formateadas
        
        if fechas_datetime:
            # Buscamos la fecha más reciente encontrada en este perfil
            fecha_mas_reciente = max(fechas_datetime)
            dias_antiguedad = (datetime.now() - fecha_mas_reciente).days
            
            # Aplicamos reglas temporales
            if dias_antiguedad <= 30:
                score_final += MATRIZ_SCORING["datos_recientes"]
                factores_de_riesgo.append("datos_recientes")
            elif dias_antiguedad >= 1095: # 3 años
                score_final += MATRIZ_SCORING["datos_viejos"]
                factores_de_riesgo.append("datos_viejos")

    roles_detectados = perfil_scraper.get("roles", [])
    if len(roles_detectados) > 0:
        score_final += MATRIZ_SCORING["rol_expuesto"]
        factores_de_riesgo.append("rol_expuesto")

    # 2. Sumar la información de infraestructura/hábitos (que viene de otro sistema)
    for clave, estado in info_interna_usuario.items():
        if estado is True and clave in MATRIZ_SCORING:
            score_final += MATRIZ_SCORING[clave]
            factores_de_riesgo.append(clave)

    return {
        "nombre_analizado": perfil_scraper.get("nombre", "Desconocido"),
        "roles_identificados": roles_detectados, 
        "score_total": max(0, score_final),
        "nivel_riesgo": calcular_nivel_riesgo(score_final),
        "factores_de_riesgo_detectados": factores_de_riesgo
    }

# === Simulación de Integración ===
# if __name__ == "__main__":
#     contexto_usuario = {
#         "mfa_desactivada": False,
#         "backup_inexistente": False
#     }

#     # Perfil 1: Datos filtrados hoy/recientemente
#     perfil_caliente = {
#         "nombre": "Sofía Martínez",
#         "emails": ["sofia@example.com"],
#         "telefonos": ["1123602360"],
#         "ubicaciones": ["Mar del Plata"],
#         "fechas": ["2026-06-30 09:18:42 UTC-3"] # Reciente
#     }
    
#     # Perfil 2: Datos filtrados hace mucho tiempo
#     perfil_frio = {
#         "nombre": "Emilia Díaz",
#         "emails": ["emilia@example.com"],
#         "telefonos": ["1143218765"],
#         "ubicaciones": ["Buenos Aires"],
#         "fechas": ["2019-08-15"] # Obsoleto
#     }

#     print("--- Perfil Reciente ---")
#     print(json.dumps(evaluar_perfil(perfil_caliente, contexto_usuario), indent=4, ensure_ascii=False))
    
#     print("\n--- Perfil Obsoleto ---")
#     print(json.dumps(evaluar_perfil(perfil_frio, contexto_usuario), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    contexto_usuario = {"mfa_desactivada": False}

    # Perfil 1: Usuario normal (Sofía)
    perfil_usuario = {
        "nombre": "Sofía Martínez",
        "emails": ["sofia@example.com"],
        "telefonos": [],
        "ubicaciones": [],
        "fechas": ["2026-07-02"],
        "roles": [] # Sin rol detectado
    }
    
    # Perfil 2: Administrador expuesto (Roberto del HTML que pasaste antes)
    perfil_admin = {
        "nombre": "Roberto Sánchez",
        "emails": ["rsanchez@photoshare.com.ar"],
        "telefonos": ["11-9999-0000"],
        "ubicaciones": [],
        "fechas": ["2026-07-02"],
        "roles": ["Administrador", "Base de Datos"] # El scrapper capturó esto
    }

    print("--- Usuario Regular ---")
    print(json.dumps(evaluar_perfil(perfil_usuario, contexto_usuario), indent=4, ensure_ascii=False))
    
    print("\n--- Administrador Expuesto (Riesgo Crítico) ---")
    print(json.dumps(evaluar_perfil(perfil_admin, contexto_usuario), indent=4, ensure_ascii=False))