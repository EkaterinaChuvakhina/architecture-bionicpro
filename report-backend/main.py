import logging
import sys
from fastapi import FastAPI
from routers.reports import router as reports_router
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]   # ← выводит в консоль Docker
)

for logger_name in ["__main__", "routers.reports", "auth_dependency", "s3_client"]:
    logging.getLogger(logger_name).setLevel(logging.INFO)

app = FastAPI(
    title="BionicPRO Reports API",
    description="API для получения готовых отчётов из OLAP",
    version="1.0.0"
)

app.include_router(reports_router)


@app.get("/")
async def root():
    return {"message": "BionicPRO Reports API is running"}