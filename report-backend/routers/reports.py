from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import io
from datetime import datetime

from dependencies import CurrentUser
from database import get_clickhouse_client
from models import UserReport

router = APIRouter(prefix="/reports", tags=["reports"])

env = Environment(loader=FileSystemLoader("templates"))

@router.get("/")
async def get_my_report_pdf(current_user: dict = CurrentUser):
    email = current_user.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Email not found")

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

    row = result.result_rows[0]
    data = dict(zip(result.column_names, row))

    template = env.get_template("report_template.html")
    html_content = template.render(data=data)

    pdf_bytes = HTML(string=html_content).write_pdf()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="report_{email.split("@")[0]}_{datetime.now().strftime("%Y%m%d")}.pdf"'
        }
    )