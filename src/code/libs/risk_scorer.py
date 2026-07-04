import json, yaml
from datetime import datetime

class RiskScorer:

    def __init__(self, config_path: str):

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            self.matriz_scoring = config.get("scoring", {})
            self.levels_riesgo = dict(sorted(config.get("levels", {}).items()))

        except Exception as e:
            raise RuntimeError(f"Error al cargar la configuración: {str(e)}")

    def evaluar_perfil(self, perfil_scraper: dict, info_interna_usuario: dict = None):
        score_final = 0
        cant_datos_expuestos = 0
        factores_de_riesgo = []

        # Score de datos de contacto expuestos (emails y teléfonos)
        score_final += self._evaluar_datos_de_contacto_expuestos(
            cant_datos_expuestos=cant_datos_expuestos,
            factores_de_riesgo=factores_de_riesgo,
            emails=perfil_scraper.get('emails'), 
            telefonos=perfil_scraper.get('telefonos')
            )

        # Verificamos exposición de nombre o ubicación
        tiene_nombre = perfil_scraper.get("nombre") and perfil_scraper.get("nombre") != "Desconocido"
        tiene_ubicacion = len(perfil_scraper.get("ubicaciones", [])) > 0
        
        if tiene_nombre or tiene_ubicacion:
            score_final += self.matriz_scoring["datos_personales_expuestos"]
            factores_de_riesgo.append("datos_personales_expuestos")
            cant_datos_expuestos += 1

        score_final += self._validar_doxing_agrupado(
            cant_datos_expuestos=cant_datos_expuestos, 
            factores_de_riesgo=factores_de_riesgo
            )

        score_final += self._calculo_time_decay(
            factores_de_riesgo=factores_de_riesgo, 
            fechas=perfil_scraper.get('fechas')
            )
        
        roles_detectados = perfil_scraper.get('roles', [])
        score_final += self._evaluar_roles_expuestos(
            factores_de_riesgo=factores_de_riesgo,
            roles=roles_detectados
            )

        if info_interna_usuario:
            for clave, estado in info_interna_usuario.items():
                if estado is True and clave in self.matriz_scoring:
                    score_final += self.matriz_scoring[clave]
                    factores_de_riesgo.append(clave)

        return {
            "nombre_analizado": perfil_scraper.get("nombre", "Desconocido"),
            "roles_identificados": roles_detectados, 
            "score_total": max(0, score_final),
            "nivel_riesgo": self._calcular_nivel_riesgo(score_final),
            "factores_de_riesgo_detectados": factores_de_riesgo
        }

    def _calcular_nivel_riesgo(self, score_total:int):
    
        for limite, nivel in self.levels_riesgo.items():
            if score_total <= limite:
                return nivel
        
        return list(self.levels_riesgo.values())[-1]

    def _evaluar_datos_de_contacto_expuestos(self, cant_datos_expuestos, factores_de_riesgo, emails, telefonos):
        
        score = 0

        if emails:
            score += self.matriz_scoring["email_expuesto"]
            factores_de_riesgo.append("email_expuesto")
            cant_datos_expuestos += 1

        if telefonos:
            score += self.matriz_scoring["telefono_expuesto"]
            factores_de_riesgo.append("telefono_expuesto")
            cant_datos_expuestos += 1

        return score

    def _calculo_time_decay(self, factores_de_riesgo, fechas):

        score = 0

        if fechas:
            fechas_datetime = []
            for f in fechas:
                try:
                    fecha_limpia = f[:10]
                    fechas_datetime.append(datetime.strptime(fecha_limpia, "%Y-%m-%d"))
                except ValueError:
                    continue # Ignoramos fechas mal formateadas
            
            if fechas_datetime:
                fecha_mas_reciente = max(fechas_datetime)
                dias_antiguedad = (datetime.now() - fecha_mas_reciente).days
                
                # Time Decay
                if dias_antiguedad <= 30:
                    score += self.matriz_scoring["datos_recientes"]
                    factores_de_riesgo.append("datos_recientes")
                elif dias_antiguedad >= 1095: # 3 años
                    score += self.matriz_scoring["datos_viejos"]
                    factores_de_riesgo.append("datos_viejos")
        
        return score

    def _evaluar_roles_expuestos(self, factores_de_riesgo, roles):
        
        score = 0

        if roles:
            score += self.matriz_scoring["rol_expuesto"]
            factores_de_riesgo.append("rol_expuesto")

        return score

    def _validar_doxing_agrupado(self, cant_datos_expuestos, factores_de_riesgo):
        
        score = 0
    
        if cant_datos_expuestos >= 3:
            score_final += self.matriz_scoring["riesgo_doxing_agrupado"]
            factores_de_riesgo.append("riesgo_doxing_agrupado")

        return score

    