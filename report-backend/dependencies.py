import httpx
from fastapi import Depends, HTTPException, Request
import os
import logging

logger = logging.getLogger("auth_dependency")
logger.setLevel(logging.DEBUG)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://bionicpro-auth:8082")

async def get_current_user(request: Request):
    jsessionid = request.cookies.get("JSESSIONID")
    session_cookie = request.cookies.get("SESSION")

    logger.info("=== AUTH CHECK START ===")
    logger.info(f"JSESSIONID: {bool(jsessionid)} | SESSION: {bool(session_cookie)}")

    if not jsessionid:
        logger.warning("No JSESSIONID cookie → 401")
        raise HTTPException(status_code=401, detail="No session cookie")

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{AUTH_SERVICE_URL}/api/auth/status",
                cookies=request.cookies,
                timeout=5.0
            )

            logger.info(f"Auth service responded: {resp.status_code}")

            if resp.status_code != 200:
                logger.error(f"Auth service error: {resp.text}")
                raise HTTPException(status_code=401, detail="Not authenticated")

            data = resp.json()

            if not data.get("authenticated"):
                raise HTTPException(status_code=401, detail="Not authenticated")

            logger.info(f"Auth OK for user: {data.get('user')} / email: {data.get('email')}")
            logger.info("=== AUTH CHECK END ===\n")

            return {
                "email": data.get("email"),
                "username": data.get("user"),
                "roles": data.get("roles", [])
            }

        except Exception as e:
            logger.error(f"Auth service call failed: {e}")
            raise HTTPException(status_code=401, detail="Auth service unavailable")

CurrentUser = Depends(get_current_user)