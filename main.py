import time
import requests 
import httpx
import asyncio

from fastapi import FastAPI

app = FastAPI(title = "P1-W03-D1: Async vs Sync I/O")

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