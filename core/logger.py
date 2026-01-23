import os
from loguru import logger

# 创建日志目录
LOG_PATH = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

# 配置日志格式与持久化
log_file = os.path.join(LOG_PATH, "api_{time:YYYY-MM-DD}.log")

logger.add(
    log_file,
    rotation="00:00",      # 每天凌晨轮转
    retention="30 days",   # 保留30天
    level="INFO",
    encoding="utf-8",
    enqueue=True,          # 异步写入
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# 导出供全局使用
app_logger = logger