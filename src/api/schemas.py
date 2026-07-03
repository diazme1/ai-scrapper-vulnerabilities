from pydantic import BaseModel


class Profile(BaseModel):

    nombre: str
    usuarios: list
    emails: list
    telefonos: list
    ubicaciones: list
    fechas: list
    roles: list
    
class ContextProfile(BaseModel):
    mfa_desactivada: bool = False
    contrasena_reutilizada: bool = False
    contrasenas_guardadas_en_navegador: bool = False
    redes_sociales_publicas: bool = False
    conexion_frecuente_a_redes_publicas: bool = False
    antivirus_desactivado: bool = False
    compras_online_frecuentes: bool = False
    backup_inexistente: bool = False   


class RiskResponse(BaseModel):

    nombre_analizado: str
    roles_identificados: list
    score_total: int
    nivel_riesgo: str
    factores_de_riesgo_detectados: list

class WebScanResponse(BaseModel):

    estado: str
    total_personas_encontradas: int
    personas: list
    tecnologias_detectadas: dict

class WebScanResponseWithRisk(WebScanResponse):

    estado: str
    total_personas_encontradas: int
    personas: list[RiskResponse]
    tecnologias_detectadas: dict