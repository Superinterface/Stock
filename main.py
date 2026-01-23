from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import auth, stock
from core.logger import app_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("量子量化系统启动中...")
    yield
    app_logger.info("系统关闭中...")

app = FastAPI(title="QuantApp", lifespan=lifespan)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stock.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)