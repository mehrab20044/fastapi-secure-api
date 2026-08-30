import asyncio
import time
from datetime import timedelta
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import httpx
from pydantic import BaseModel
import requests

# وارد کردن ابزارهای امنیتی از auth.py
from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI(
    title = "P1-W03-D1: Async vs Sync I/O",
    description="پروژه یادگیری فاز ۱: تست همزمانی Async/Sync + احراز هویت JWT",
    version="1.0.0"
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
        response = requests.get(url)
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

    async with httpx.AsyncClient() as client:
        for url in URLS:
            response = await client.get(url)
            resulte.append(response.json())

        duration = time.perf_counter() - start_time

        return{
            "mode": "Async_sequential",
            "total_request": len(resulte),
            "duration_seconds": round(duration, 3),
        }

@app.get("/async-concurrent")
async def async_concurrent():
    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in URLS]
        response = await asyncio.gather(*tasks)

        resulte = [resp.json() for resp in response]

        duration = time.perf_counter() - start_time

        return {
        "mode": "async_concurrent",
        "total_requests": len(resulte),
        "duration_seconds": round(duration, 3),
    }  


fake_users_db = {
    "mehrab":{
        "username": "mehrab",
        "full_name": "Mehrab Backend Dev",
        "email": "mehrab.5511.m3709@gmail.com",
        "hashed_password": get_password_hash("ai_mentor_2026"),
    }
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
async def read_users_me(current_username: str = Depends(get_current_user)):
    user = fake_users_db.get(current_username)
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
    }
    