# dependencies.py
from fastapi import Depends, HTTPException, status, Request
import requests
import os
from typing import Dict

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8081")


async def get_current_user(request: Request):
    """
    Проверяет JSESSIONID сессию через Spring Boot Auth сервис
    """
    # Берём JSESSIONID из куки (FastAPI автоматически получает куки из запроса)
    jsessionid = request.cookies.get("JSESSIONID")

    if not jsessionid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session cookie found"
        )

    try:
        # Делаем запрос к Spring Boot для проверки сессии
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/status",
            cookies={"JSESSIONID": jsessionid},
            timeout=5
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )

        user_info: Dict = response.json()

        if not user_info.get("authenticated"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found in user info"
            )

        # Возвращаем информацию о пользователе
        return {
            "email": email,
            "username": user_info.get("user"),
            "roles": user_info.get("roles", [])
        }

    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service is unavailable"
        )


# Удобный alias для Depends
CurrentUser = Depends(get_current_user)