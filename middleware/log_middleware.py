import time
from fastapi import Request
from core.logger import app_logger


async def log_request_middleware(request: Request, call_next):
    start_time = time.time()

    # 获取请求详情
    client_ip = request.client.host
    method = request.method
    url = request.url.path

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    formatted_time = f"{process_time:.2f}ms"

    # 持久化记录
    app_logger.info(
        f"IP: {client_ip} | Method: {method} | URL: {url} | "
        f"Status: {response.status_code} | ProcessTime: {formatted_time}"
    )

    return response