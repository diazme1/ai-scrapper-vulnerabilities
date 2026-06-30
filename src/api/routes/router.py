from fastapi import APIRouter
from src.code.libs import RiskClassifier
from src.api.schemas import Profile, RiskResponse

router = APIRouter()

risk_classifier = RiskClassifier()


@router.post("/procesar-perfil", response_model=RiskResponse)
def procesar_perfil(profile: Profile):

    return risk_classifier.process_profile(profile)

