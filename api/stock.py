from fastapi import APIRouter, Query
from typing import Optional
import db.DBUtil as dbUtil
import pandas as pd

router = APIRouter(prefix="/api/stock", tags=["数据"])


@router.get("/history")
async def get_history(
        symbol: str,
        start_date: Optional[str] = Query(None),
        end_date: Optional[str] = Query(None)
):
    # 基础 SQL
    sql = "SELECT vc_date, n_open_price, n_close_price, n_low_price, n_hight_price FROM stock.stock_history WHERE 1=1"

    # 动态拼接查询条件
    params = {"symbol": symbol}
    sql += " AND vc_symbol = :symbol"

    if start_date:
        sql += " AND vc_date >= :start_date"
        params["start_date"] = start_date

    if end_date:
        sql += " AND vc_date <= :end_date"
        params["end_date"] = end_date

    sql += " ORDER BY vc_date ASC"

    # 使用 SQLAlchemy 的参数化查询防止注入 (推荐做法)
    from sqlalchemy import text
    with dbUtil.postgre_engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)

    df['vc_date'] = df['vc_date'].astype(str)
    return df.to_dict(orient="records")

@router.get("/list")
async def get_stock_list():
    # 实际开发中建议从数据库 sys_stock_base 这种基础信息表查询
    # 这里模拟返回数据
    sql = "SELECT vc_symbol as value, vc_name as label FROM stock.stock_info"
    try:
        df = pd.read_sql(sql, dbUtil.postgre_engine)
        # 构造混合标签： "000001 平安银行" 方便前端全文检索
        df['search_text'] = df['value'] + " " + df['label']
        return df.to_dict(orient="records")
    except:
        return [{"value": "000001", "label": "平安银行", "search_text": "000001 平安银行"}]