from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="AI Scrapper Vulnerabilities API",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1, 
        "syntaxHighlight.theme": "obsidian"}
)

app.include_router(router)