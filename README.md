# FastAPI Async vs Sync Benchmark

This project demonstrates the performance differences between Synchronous I/O, Asynchronous Sequential I/O, and Asynchronous Concurrent I/O in FastAPI.

## Benchmark Results (5 HTTP Requests)

| Execution Mode | Mechanism | Duration |
| :--- | :--- | :--- |
| **Sync** | `requests.get` (Blocking) | ~2.85s |
| **Async Sequential** | `httpx.AsyncClient` with sequential `await` | ~1.67s |
| **Async Concurrent** | `httpx.AsyncClient` + `asyncio.gather` | **~0.51s** 🚀 |

## How to Run

1. Create and activate virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
   
