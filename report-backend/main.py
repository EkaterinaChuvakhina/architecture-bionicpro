from fastapi import FastAPI
from routers.reports import router as reports_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BionicPRO Reports API",
    description="API для получения готовых отчётов из OLAP",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(reports_router)


@app.get("/")
async def root():
    return {"message": "BionicPRO Reports API is running"}
