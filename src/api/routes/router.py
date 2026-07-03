from fastapi import APIRouter, UploadFile, File, Form
from src.code.libs import Scrapper, RiskScorer
from src.api.schemas import Profile, RiskResponse, WebScanResponse, ContextProfile

router = APIRouter()

scrapper = Scrapper()
risk_scorer = RiskScorer(config_path="src/config/matriz_scores.yaml")


@router.post("/escanear-web", response_model=WebScanResponse)
def escanear_web(url: str):

    response = scrapper.escanear_web(url, True)

    return response

@router.post("/escanear-html", response_model=WebScanResponse)
async def escanear_html(html_file: UploadFile = File(...)):

    content = await html_file.read()
    html_content = content.decode("utf-8")

    response = scrapper.escanear_web(html_content, False)

    return response

@router.post("/evaluar-perfil", response_model=RiskResponse)
def evaluar_perfil(profile: Profile):

    perfil_scraper = profile.dict()

    resultado = risk_scorer.evaluar_perfil(perfil_scraper)

    return resultado

