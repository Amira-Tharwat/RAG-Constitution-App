"""
TIP: This is the main entry point of the FastAPI application. 
Implement the FastAPI app and integrate routers and databases here according to the README.
"""

from fastapi import FastAPI
from routes.data import data_router
from routes.nlp import nlp_router
from helpers import get_settings

settings = get_settings()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


app.include_router(data_router)
app.include_router(nlp_router)

@app.get("/api/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} v{settings.APP_VERSION} is Running!"}