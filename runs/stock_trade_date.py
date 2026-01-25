import datetime
import pandas as pd
import akshare as ak
from sqlalchemy import insert, delete
import db.DBUtil as dbUtil
import table_model.StockTradeDate as std


def sync_stock_trade_date():
    print("--- 正在同步交易日列表 ---")
    # 1. 获取数据
    df = ak.tool_trade_date_hist_sina()

    # 2. 数据清洗
    # AkShare 返回的是 trade_date，需要重命名为数据库对应的字段名（假设是 d_date）
    df = df.rename(columns={'trade_date': 'd_date'})
    # 转换为日期格式
    df['d_date'] = pd.to_datetime(df['d_date']).dt.date
    df['vc_is_trade'] = 1


    with dbUtil.postgre_engine.connect() as conn:
        with conn.begin():
            # 3. 物理清空：交易日属于基础表，直接全量清空最安全
            conn.execute(delete(std.stock_trade_date))

            # 4. 批量插入
            # orient="records" 生成的 [{d_date: ...}, {d_date: ...}] 格式
            data_dict = df.to_dict(orient="records")
            conn.execute(insert(std.stock_trade_date), data_dict)

    print(f"--- 同步完成，共记录 {len(df)} 个交易日 ---")


if __name__ == "__main__":
    sync_stock_trade_date()