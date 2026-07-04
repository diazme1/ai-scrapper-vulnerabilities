from fastapi import APIRouter, UploadFile, File, Form
from src.code.libs import Scrapper, RiskScorer
from src.api.schemas import Profile, RiskResponse, WebScanResponse, ContextProfile, WebScanResponseWithRisk

router = APIRouter()

scrapper = Scrapper()
risk_scorer = RiskScorer(config_path="src/config/matriz_scores.yaml")


@router.post("/escanear-web", response_model=WebScanResponse, tags=["Scrapper Web"])
def escanear_web(url: str):

    response = scrapper.escanear_web(url, True)

    return response

@router.post("/escanear-html", response_model=WebScanResponse, tags=["Scrapper Web"])
async def escanear_html(html_file: UploadFile = File(...)):

    content = await html_file.read()
    html_content = content.decode("utf-8")

    response = scrapper.escanear_web(html_content, False)

    return response

@router.post("/evaluar-perfil", response_model=RiskResponse, tags=["Risk Scorer"])
def evaluar_perfil(profile: Profile):
    # Evalua sin contexto
    perfil_scraper = profile.dict()

    response = risk_scorer.evaluar_perfil(perfil_scraper)

    return response

@router.post("/evaluar-perfil-contexto", response_model=RiskResponse, tags=["Risk Scorer"])
def evaluar_perfil_con_contexto(profile: Profile, contexto: ContextProfile):

    perfil_scraper = profile.dict()
    info_interna = contexto.dict()

    response = risk_scorer.evaluar_perfil(perfil_scraper, info_interna_usuario=info_interna)

    return response

@router.post("/escanear-perfiles-html", response_model=WebScanResponse, tags=["Scrapper y Risk Scorer"])
async def escanear_perfiles_html(html_file: UploadFile = File(...)):

    content = await html_file.read()
    html_content = content.decode("utf-8")

    response = scrapper.escanear_web(html_content, False)

    for persona in response.get("personas", []):
        risk_response = risk_scorer.evaluar_perfil(persona)
        persona["evaluación_riesgo"] = risk_response

    return response

@router.post("/escanear-perfiles-url", response_model=WebScanResponse, tags=["Scrapper y Risk Scorer"])
async def escanear_perfiles_url(url: str):

    response = scrapper.escanear_web(url, True)

    for persona in response.get("personas", []):
        risk_response = risk_scorer.evaluar_perfil(persona)
        persona["evaluación_riesgo"] = risk_response

    return response
