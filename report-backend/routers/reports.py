from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import logging
import time

from dependencies import CurrentUser
from database import get_clickhouse_client
from s3_client import get_presigned_url, upload_report_to_s3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])

env = Environment(loader=FileSystemLoader("templates"))


@router.get("/")
async def get_my_report(current_user: dict = CurrentUser):
    email = current_user.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Email not found")

    start_time = time.time()
    logger.info(f"Запрос отчёта для email: {email}")

    presigned_url = get_presigned_url(email)

    if presigned_url:
        duration = time.time() - start_time
        logger.info(f"Отчёт из S3 (MinIO) за {duration:.2f} сек")
        logger.info(f"Пользователь: {email} | Ссылка готова")
    else:
        logger.info(f"Отчёт не найден в S3 → начинаем генерацию для {email}")
        try:
            client = get_clickhouse_client()

            query = """
                    SELECT *
                    FROM bionicpro.user_prosthesis_report_cdc
                    WHERE email = %(email)s
                    ORDER BY updated_at DESC LIMIT 1 \
                    """

            result = client.query(query, parameters={'email': email})

            if not result.result_rows:
                logger.warning(f"Нет данных в ClickHouse для {email}")
                raise HTTPException(status_code=404, detail=f"Report for {email} not found")

            data = dict(zip(result.column_names, result.result_rows[0]))

            template = env.get_template("report_template.html")
            html_content = template.render(data=data)
            pdf_bytes = HTML(string=html_content).write_pdf()

            upload_report_to_s3(pdf_bytes, email)
            presigned_url = get_presigned_url(email)

            logger.info(f"Отчёт УСПЕШНО СГЕНЕРИРОВАН и загружен в S3")

        except Exception as e:
            logger.error(f"Ошибка генерации отчёта для {email}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

    logger.info(f"Возвращаем download_url для {email}\n")
    return {"download_url": presigned_url}
