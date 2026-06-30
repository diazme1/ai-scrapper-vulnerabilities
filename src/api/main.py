from fastapi import FastAPI
from app.api.risk import router

app = FastAPI(
    title="Attack Surface Risk Classifier",
    version="1.0.0"
)

app.include_router(router)