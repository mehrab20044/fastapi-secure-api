import asyncio
import time
from datetime import timedelta

import httpx
import requests
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

# وارد کردن ابزارهای امنیتی از auth.py
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from database import get_db

app = FastAPI(
    title = "P1-W03: Async vs Sync I/O",
    description="پروژه یادگیری فاز ۱: تست همزمانی Async/Sync + احراز هویت JWT",
    version="1.0.0"
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request,
    exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error":{
            "status_code": exc.status_code,
            "message": exc.detail,
        },
    },
    headers=exc.headers,
    )

URLS = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
    "https://jsonplaceholder.typicode.com/posts/4",
    "https://jsonplaceholder.typicode.com/posts/5",
]

@app.get("/sync-fetch")
def sync_fetch():
    start_time = time.perf_counter()
    results = []

    for url in URLS:
        response = requests.get(url, timeout=5.0)
        response.raise_for_status()
        results.append(response.json())

    duration = time.perf_counter() - start_time
    return {
        "mode": "sync",
        "total_requests": len(results),
        "duration_seconds": round(duration, 3),
    }

@app.get("/async-fetch")
async def async_fetch():
    start_time = time.perf_counter()
    resulte = []

    timeout = httpx.Timeout(5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        for url in URLS:
            response = await client.get(url)
            response.raise_for_status()
            resulte.append(response.json())

        duration = time.perf_counter() - start_time

        return{
            "mode": "Async_sequential",
            "total_request": len(resulte),
            "duration_seconds": round(duration, 3),
        }

async def fetch_one(client: httpx.AsyncClient, url: str) -> dict:
    try:
        response = await client.get(url)
        response.raise_for_status()

        return {
            "url": url,
            "ok": True,
            "status_code": response.status_code,
            "data": response.json(),
        }

    except httpx.TimeoutException:
        return {
            "url": url,
            "ok": False,
            "error": "timeout",
        }

    except httpx.HTTPStatusError as exc:
        return {
            "url": url,
            "ok": False,
            "status_code": exc.response.status_code,
            "error": "http_error",
        }

    except httpx.RequestError as exc:
        return {
            "url": url,
            "ok": False,
            "error": type(exc).__name__,
        }




@app.get("/async-concurrent")
async def async_concurrent():
    start_time = time.perf_counter()
    timeout = httpx.Timeout(5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [fetch_one(client, url) for url in URLS]
        results = await asyncio.gather(*tasks)

    duration = time.perf_counter() - start_time
    successful_requests = sum(result["ok"] for result in results)
    failed_requests = len(results) - successful_requests

    return {
        "mode": "async_concurrent",
        "total_requests": len(results),
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "duration_seconds": round(duration, 3),
        "results": results,
    } 


fake_users_db = {
    "mehrab":{
        "username": "mehrab",
        "full_name": "Mehrab Backend Dev",
        "email": "mehrab.5511.m3709@gmail.com",
        "hashed_password": get_password_hash("ai_mentor_2026"),
        "role": "user",
    },
    "admin":{
        "username": "admin",
        "full_name": "Mehrab Backend Dev",
        "email": "admin.5511.m3709@gmail.com",
        "hashed_password": get_password_hash("admin_2026"),
        "role": "admin",
        },
}


async def require_admin(
    current_username: str = Depends(get_current_user),      
):
    user = fake_users_db.get(current_username)

    if not user or user ["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= "Admin access required"
        )
    return user

@app.get("/admin")
async def admin_panel(
    current_user: dict = Depends(require_admin),
):
    return{
        "message": "welcom admin",
        "username": current_user["username"],
        "role": current_user["role"]
    }


class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me")
async def read_users_me(
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.execute(text("SELECT 1"))

    user = fake_users_db.get(current_username)

    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
    }