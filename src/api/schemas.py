from pydantic import BaseModel


class Profile(BaseModel):

    email_expuesto: bool
    phone_expuesto: bool
    mfa_desactivada: bool
    password_filtrada: bool
    github_publico: bool
    secrets_in_repo: bool
    api_keys_expuestas: bool
    software_expirado: bool
    tls_expirado: bool
    http_solo: bool
    dns_mal_configurado: bool
    docs_publicos: bool
    ssh_expuesto: bool
    rdp_expuesto: bool
    bucket_publico: bool
    cves: int
    failed_security_headers: int

class RiskResponse(BaseModel):

    risk_level: str
    risk_score: float

class WebScanResponse(BaseModel):

    estado: str
    total_personas_encontradas: int
    personas: list