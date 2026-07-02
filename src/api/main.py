from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="AI Scrapper Vulnerabilities API",
    version="1.0.0"
)

app.include_router(router)