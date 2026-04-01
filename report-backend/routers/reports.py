from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

from dependencies import CurrentUser
from database import get_clickhouse_client
from s3_client import get_presigned_url, upload_report_to_s3

router = APIRouter(prefix="/reports", tags=["reports"])

env = Environment(loader=FileSystemLoader("templates"))


@router.get("/")
async def get_my_report(current_user: dict = CurrentUser):
    email = current_user.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Email not found")

    presigned_url = get_presigned_url(email)

    if not presigned_url:
        try:
            client = get_clickhouse_client()

            query = """
                SELECT * FROM bionicpro.user_prosthesis_report 
                WHERE email = %(email)s 
                ORDER BY updated_at DESC 
                LIMIT 1
            """

            result = client.query(query, parameters={'email': email})

            if not result.result_rows:
                raise HTTPException(status_code=404, detail=f"Report for {email} not found")

            data = dict(zip(result.column_names, result.result_rows[0]))

            template = env.get_template("report_tkemplate.html")
            html_content = template.render(data=data)
            pdf_bytes = HTML(string=html_content).write_pdf()

            upload_report_to_s3(pdf_bytes, email)
            presigned_url = get_presigned_url(email)

        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to generate report")

    return {"download_url": presigned_url}