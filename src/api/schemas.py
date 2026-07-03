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
    
    info_interna_usuario: dict    


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