import datetime
import time
import pandas as pd
import akshare as ak
from sqlalchemy import insert, delete, text
from sqlalchemy.dialects.postgresql import insert as pg_upsert
import db.DBUtil as dbUtil
import table_model.StockListA as stock_list
import table_model.StockHistory as history
import table_model.StockSyncStatus as sync_status


def save_single_stock_history(symbol: str, start_date: str, end_date: str):
    """获取单只股票行情并更新状态表"""
    ak_start = start_date.replace("-", "")
    ak_end = end_date.replace("-", "")

    try:
        # 1. 网络请求
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=ak_start, end_date=ak_end, adjust="")
        if df.empty:
            # 即便为空也更新同步时间，防止死循环重复抓取无数据的股票
            _update_status_table(symbol, start_date, start_date)
            return True

        # 2. 数据清洗 (保持你之前的 rename 逻辑)
        df.rename(columns={
            "日期": "vc_date", "股票代码": "vc_symbol", "开盘": "n_open_price",
            "收盘": "n_close_price", "最高": "n_hight_price", "最低": "n_low_price",
            "成交量": "n_trading_num", "成交额": "n_trading_amount", "振幅": "n_amplitude",
            "涨跌幅": "n_price_range", "涨跌额": "n_price_change", "换手率": "n_change_hands",
        }, inplace=True)
        df['vc_data_source'] = 'stock_zh_a_hist-东方财富'
        df['vc_create_date'] = datetime.datetime.now()

        # 3. 数据库事务：删除旧数据 -> 插入新数据 -> 更新状态
        with dbUtil.postgre_engine.connect() as conn:
            with conn.begin():
                # 删除当前抓取区间的数据
                conn.execute(delete(history.stock_history).where(
                    history.stock_history.c.vc_date.between(start_date, end_date),
                    history.stock_history.c.vc_symbol == symbol
                ))
                # 批量插入
                conn.execute(insert(history.stock_history), df.to_dict(orient="records"))

                # 4. PostgreSQL UPSERT 更新状态表
                stmt = pg_upsert(sync_status.stock_sync_status).values(
                    vc_symbol=symbol,
                    d_min_date=df['vc_date'].min(),
                    d_max_date=df['vc_date'].max(),
                    d_last_sync_time=datetime.datetime.now()
                ).on_conflict_do_update(
                    index_elements=['vc_symbol'],
                    set_={
                        'd_min_date': text("LEAST(stock_sync_status.d_min_date, EXCLUDED.d_min_date)"),
                        'd_max_date': text("GREATEST(stock_sync_status.d_max_date, EXCLUDED.d_max_date)"),
                        'd_last_sync_time': datetime.datetime.now()
                    }
                )
                conn.execute(stmt)

        print(f"  [OK] {symbol} 同步完成 ({len(df)}条)")
        return True
    except Exception as e:
        print(f"  [Error] {symbol} 失败: {e}")
        return False


def _update_status_table(symbol, min_d, max_d):
    """辅助方法：仅更新同步时间"""
    with dbUtil.postgre_engine.connect() as conn:
        stmt = pg_upsert(sync_status.stock_sync_status).values(
            vc_symbol=symbol, d_min_date=min_d, d_max_date=max_d, d_last_sync_time=datetime.datetime.now()
        ).on_conflict_do_update(
            index_elements=['vc_symbol'],
            set_={'d_last_sync_time': datetime.datetime.now()}
        )
        conn.execute(stmt)
        conn.commit()


def batch_update_history():
    """主调度逻辑"""
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    # 核心 SQL：寻找从未同步过，或者最后同步时间不是今天的股票
    sql = text("""
               SELECT a.vc_symbol_code, a.vc_list_date
               FROM stock.stock_list_a a
                        LEFT JOIN stock.stock_sync_status s ON a.vc_symbol_code = s.vc_symbol
               WHERE s.d_last_sync_time IS NULL
                  OR s.d_last_sync_time < CURRENT_DATE
               ORDER BY a.vc_symbol_code ASC
               """)

    with dbUtil.postgre_engine.connect() as conn:
        stocks = conn.execute(sql).fetchall()

    print(f"发现 {len(stocks)} 只股票需要同步行情...")

    fail_count = 0
    for row in stocks:
        symbol, list_date = row[0], str(row[1])
        if list_date > yesterday: continue

        success = save_single_stock_history(symbol, list_date, yesterday)

        if not success:
            fail_count += 1
        else:
            fail_count = 0  # 成功则重置失败计数

        # 连续失败 2 次，判定为 IP 被封或网络故障，自动熔断
        if fail_count >= 2:
            print("!!! 连续多次请求失败，可能已被封禁 IP，程序自动退出 !!!")
            break

        time.sleep(120)  # 控制频率


if __name__ == "__main__":
    batch_update_history()