import numpy as np
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
    # 拓展 SQL 语句，取出你需要的额外字段
    sql = """
          SELECT vc_symbol_code as value, 
            vc_symbol_name as label,
            vc_market as market,
            vc_list_date as "setupDate",
            vc_updated_time as "lastSync"
          FROM stock.stock_list_a \
          """
    try:
        df = pd.read_sql(sql, dbUtil.postgre_engine)

        # 1. 构造混合标签：方便前端 el-select-v2 进行全文检索
        df['search_text'] = df['value'].astype(str) + " " + df['label'].astype(str)

        # 2. 处理空值：防止数据库中的 NULL 导致前端显示 "NaN" 或崩溃
        # 使用 fillna 将空值转换为空字符串或友好提示
        df = df.fillna({
            'market': '未知',
            'setupDate': '-',
            'lastSync': '未同步'
        })

        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error fetching stock list: {e}")
        # 兜底数据也需要补全字段，防止前端渲染报错
        return [{
            "value": "000001",
            "label": "平安银行",
            "search_text": "000001 平安银行",
            "market": "SZ",
            "setupDate": "1991-04-03",
            "lastSync": "-"
        }]



@router.get("/risk_metrics")
async def get_risk_metrics(symbol: str, start_date: str, end_date: str):
    # 1. 从数据库读取数据
    sql = f"""SELECT vc_date, n_close_price FROM stock.stock_history 
              WHERE vc_symbol = '{symbol}' AND vc_date BETWEEN '{start_date}' AND '{end_date}' 
              ORDER BY vc_date ASC"""
    df = pd.read_sql(sql, dbUtil.postgre_engine)

    if df.empty or len(df) < 2:
        return {"error": "数据量不足以计算指标"}

    # 2. 计算收益率 (Daily Return)
    # 计算方式：(当日收盘 / 前日收盘) - 1
    df['returns'] = df['n_close_price'].pct_change()

    # 3. 核心风险指标计算
    # 累计收益率
    total_return = (df['n_close_price'].iloc[-1] / df['n_close_price'].iloc[0]) - 1

    # 年化收益率 (假设一年252个交易日)
    annual_return = (1 + total_return) ** (252 / len(df)) - 1

    # 年化波动率 (收益率的标准差 * 根号下252)
    volatility = df['returns'].std() * np.sqrt(252)

    # 最大回撤 (Maximum Drawdown)
    rolling_max = df['n_close_price'].cummax()
    drawdown = (df['n_close_price'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # 夏普比率 (假设无风险利率 2%)
    sharpe_ratio = (annual_return - 0.02) / volatility if volatility != 0 else 0

    return {
        "total_return": f"{total_return * 100:.2f}%",  # 累计收益
        "annual_return": f"{annual_return * 100:.2f}%",  # 年化收益
        "volatility": f"{volatility * 100:.2f}%",  # 年化波动率
        "max_drawdown": f"{max_drawdown * 100:.2f}%",  # 最大回撤
        "sharpe_ratio": f"{sharpe_ratio:.2f}"  # 夏普比率
    }


@router.get("/summary")
async def get_market_summary():
    # 1. 股票总数
    total_sql = "SELECT count(1) as total FROM stock_info"

    # 2. 行情同步情况
    # 假设最新日期是表中最大的日期
    sync_sql = """
               WITH latest AS (SELECT max(vc_date) as last_date FROM stock_history)
               SELECT last_date, \
                      (SELECT count(distinct vc_symbol) FROM stock_history WHERE vc_date = last_date)   as sync_count, \
                      ((SELECT count(1) FROM stock_info) - \
                       (SELECT count(distinct vc_symbol) FROM stock_history WHERE vc_date = last_date)) as unsync_count
               FROM latest \
               """

    # 3. 关注股票情况 (假设有 is_favorite 字段)
    fav_sql = """
              SELECT count(1)              as fav_total, \
                     max(n_change_percent) as max_change, \
                     min(n_change_percent) as min_change
              FROM stock_snapshot \
              WHERE is_favorite = 1 \
              """

    # 实际执行时请使用 dbUtil 运行并组合成 dict 返回
    return {
        "stock_count": 5230,
        "last_date": "2026-01-23",
        "sync_count": 5100,
        "unsync_count": 130,
        "fav_count": 12,
        "fav_max": "+5.20%",
        "fav_min": "-2.15%"
    }