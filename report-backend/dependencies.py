import httpx
from fastapi import Depends, HTTPException, status, Request
import requests
import os
import logging
import traceback
from typing import Dict

# Настраиваем подробное логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("auth_dependency")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://bionicpro-auth:8082")

# async def get_current_user(request: Request):
#     jsessionid = request.cookies.get("JSESSIONID")
#
#     logger.info("=" * 80)
#     logger.info("=== AUTH DEPENDENCY STARTED ===")
#     logger.info(f"Request URL: {request.url}")
#     logger.info(f"JSESSIONID present: {bool(jsessionid)} | Value: {jsessionid[:15] if jsessionid else None}...")
#
#     if not jsessionid:
#         logger.warning("No JSESSIONID cookie found → 401")
#         raise HTTPException(status_code=401, detail="No JSESSIONID cookie found")
#
#     try:
#         logger.info(f"→ Calling auth service: {AUTH_SERVICE_URL}/api/auth/status")
#
#         response = requests.get(
#             f"{AUTH_SERVICE_URL}/api/auth/status",
#             cookies={"JSESSIONID": jsessionid},
#             timeout=10
#         )
#
#         logger.info(f"← Auth service responded with status: {response.status_code}")
#         logger.debug(f"Auth service body: {response.text[:700]}")
#
#         if response.status_code != 200:
#             logger.error(f"Auth service returned non-200 status: {response.status_code}")
#             raise HTTPException(
#                 status_code=401,
#                 detail=f"Auth service returned {response.status_code}"
#             )
#
#         user_info: Dict = response.json()
#         logger.info(f"User info received: {user_info}")
#
#         if not user_info.get("authenticated"):
#             logger.warning("User is not authenticated according to auth service")
#             raise HTTPException(status_code=401, detail="User not authenticated")
#
#         logger.info(f"Authentication SUCCESS for email: {user_info.get('email')}")
#         logger.info("=" * 80)
#
#         return {
#             "email": user_info.get("email"),
#             "username": user_info.get("username"),
#             "roles": user_info.get("roles", [])
#         }
#
#     except requests.RequestException as e:
#         logger.error(f"Connection error to auth service: {e}")
#         raise HTTPException(status_code=503, detail="Auth service is unavailable")
#     except HTTPException as e:
#         logger.error(f"HTTPException: {e.detail}")
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected exception: {type(e).__name__}: {e}")
#         logger.error(traceback.format_exc())   # ← Вот это добавит полный стек
#         raise HTTPException(status_code=500, detail="Internal authentication error")

async def get_current_user(request: Request):
    # Делаем запрос к auth-service с передачей cookie
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{AUTH_SERVICE_URL}/api/auth/userinfo",
            cookies=request.cookies,   # передаём все cookies (JSESSIONID)
            timeout=5.0
        )
        if resp.status_code != 200:
            raise HTTPException(401, "Not authenticated")
        return resp.json()


CurrentUser = Depends(get_current_user)