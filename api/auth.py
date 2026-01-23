from fastapi import APIRouter, HTTPException
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["认证"])

SECRET_KEY = "quant_secret_666"

@router.post("/login")
async def login(data: dict):
    # 演示用：实际应查询数据库
    if data.get("username") == "admin" and data.get("password") == "admin123":
        payload = {
            "sub": data["username"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="用户名或密码错误")