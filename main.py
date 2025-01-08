from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import config
from api.router import router as api_router
from database import Base, engine, SessionLocal
# from ocr import perform_ocr

# whitelist alloed routes
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5432",
]

# Create the FastAPI app instance
app = FastAPI(
    title=config.APP_TITLE,
    description=config.APP_DESCRIPTION,
)

# cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mounting static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_status():
    return {"Status": "Active"}

# Include the API router
app.include_router(api_router, prefix="/api/v1")
