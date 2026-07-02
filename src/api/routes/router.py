from fastapi import APIRouter, UploadFile, File, Form
from src.code.libs import Scrapper
from src.api.schemas import Profile, RiskResponse, WebScanResponse

router = APIRouter()

scrapper = Scrapper()


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

