import datetime
import time
import pandas as pd
import akshare as ak
from sqlalchemy import insert, delete, text
from sqlalchemy.dialects.postgresql import insert as pg_upsert

# 导入项目关联模块
import db.DBUtil as dbUtil
import table_model.StockHistory as history
import table_model.StockSyncStatus as sync_status

# ================= 熔断配置 =================
# 全局冷却记录：{ "接口名称": 解禁时间datetime }
INTERFACE_COOLDOWN = {
    "东财": datetime.datetime.min,
    "新浪": datetime.datetime.min,
    "腾讯": datetime.datetime.min
}
COOLDOWN_SECONDS = 30  # 熔断时长：5分钟


class StockDataFetcher:
    """AkShare 核心行情接口封装"""

    @staticmethod
    def get_eastmoney(symbol: str, start: str, end: str):
        """来源1：东方财富 (stock_zh_a_hist)"""
        symbol = symbol.replace("sz", "").replace("sh", "").replace("sh", "")
        df = ak.stock_zh_a_hist(
            symbol=symbol, period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""), adjust=""
        )
        mapping = {
            "日期": "vc_date", "开盘": "n_open_price", "收盘": "n_close_price",
            "最高": "n_hight_price", "最低": "n_low_price", "成交量": "n_trading_num",
            "成交额": "n_trading_amount", "振幅": "n_amplitude", "涨跌幅": "n_price_range",
            "涨跌额": "n_price_change", "换手率": "n_change_hands"
        }
        return df, mapping, "东财"

    @staticmethod
    def get_sina(symbol: str, start: str, end: str):
        """来源2：新浪财经 (stock_zh_a_daily)"""
        #prefix = "sh" if symbol.startswith(('6', '9', '5')) else "sz"
        df = ak.stock_zh_a_daily(
            #symbol=prefix + symbol,
            symbol= symbol,
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""), adjust=""
        )
        mapping = {
            "date": "vc_date", "open": "n_open_price", "close": "n_close_price",
            "high": "n_hight_price", "low": "n_low_price", "volume": "n_trading_num",
            "amount": "n_trading_amount"
        }
        return df, mapping, "新浪"

    @staticmethod
    def get_tencent(symbol: str, start: str, end: str):
        """来源3：腾讯财经 (stock_zh_a_hist_tx)"""
        #prefix = "sh" if symbol.startswith(('6', '9', '5')) else "sz"
        df = ak.stock_zh_a_hist_tx(
            #symbol=prefix + symbol,
            symbol= symbol,
            start_date=start, end_date=end, adjust=""
        )
        mapping = {
            "date": "vc_date", "open": "n_open_price", "close": "n_close_price",
            "high": "n_hight_price", "low": "n_low_price", "amount": "n_trading_amount"
        }
        return df, mapping, "腾讯"


# ================= 逻辑处理工具 =================

def is_interface_locked(name):
    """检查接口是否正在冷却"""
    now = datetime.datetime.now()
    if now < INTERFACE_COOLDOWN.get(name, datetime.datetime.min):
        remaining = (INTERFACE_COOLDOWN[name] - now).seconds
        print(f"  [Lock] {name} 冷却中，剩余 {remaining}s")
        return True
    return False


def lock_interface(name):
    """触发熔断"""
    INTERFACE_COOLDOWN[name] = datetime.datetime.now() + datetime.timedelta(seconds=COOLDOWN_SECONDS)
    print(f"  [Burn] !!! {name} 接口异常，熔断 {COOLDOWN_SECONDS} 秒 !!!")


def process_and_save(df, mapping, source_name, symbol, start_date, end_date):
    """通用清洗与入库"""
    if df is None or df.empty:
        return False

    try:
        now_time = datetime.datetime.now()
        df = df.rename(columns=mapping)
        df['vc_symbol'] = symbol
        df['vc_data_source'] = f"AkShare-{source_name}"
        df['d_create_date'] = now_time  # 对应行情表创建时间
        df['vc_date'] = pd.to_datetime(df['vc_date']).dt.strftime('%Y-%m-%d')

        with dbUtil.postgre_engine.connect() as conn:
            with conn.begin():
                # 1. 行情数据覆盖插入
                conn.execute(delete(history.stock_history).where(
                    history.stock_history.c.vc_date.between(start_date, end_date),
                    history.stock_history.c.vc_symbol == symbol
                ))
                conn.execute(insert(history.stock_history), df.to_dict(orient="records"))

                # 2. 状态表更新（重点：更新 d_last_sync_time）
                stmt = pg_upsert(sync_status.stock_sync_status).values(
                    vc_symbol=symbol.replace("sz", "").replace("sh", "").replace("bj", ""),
                    d_min_date=df['vc_date'].min(),
                    d_max_date=df['vc_date'].max(),
                    d_last_sync_time=now_time
                ).on_conflict_do_update(
                    index_elements=['vc_symbol'],
                    set_={
                        'd_min_date': text("LEAST(stock_sync_status.d_min_date, EXCLUDED.d_min_date)"),
                        'd_max_date': text("GREATEST(stock_sync_status.d_max_date, EXCLUDED.d_max_date)"),
                        'd_last_sync_time': now_time
                    }
                )
                conn.execute(stmt)
        return True
    except Exception as e:
        print(f"    [Error] {source_name} 数据入库失败: {e}")
        return False


def sync_single_stock(symbol, start, end):
    """带熔断轮询的同步任务"""
    fetch_queue = [
        #(StockDataFetcher.get_eastmoney, "东财"),
        (StockDataFetcher.get_sina, "新浪"),
        (StockDataFetcher.get_tencent, "腾讯")
    ]

    for fetch_method, name in fetch_queue:
        if is_interface_locked(name):
            continue

        try:
            df, mapping, source_name = fetch_method(symbol, start, end)
            if process_and_save(df, mapping, source_name, symbol, start, end):
                print(f"使用:{source_name} 同步成功:{symbol}")
                return True
        except Exception as e:
            print(f"  [Fail] {symbol} 在 {name} 尝试失败: {e}")
            lock_interface(name)  # 触发 5 分钟锁
            continue
    return False


# ================= 主调度程序 =================

def batch_update_history():
    """主程序入口"""
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    sql = text("""
                WITH last_trade_day AS (
                    -- 1. 找到距离今天最近的前一个交易日
                    SELECT MAX(d_date) as last_day 
                    FROM stock.stock_trade_date 
                    WHERE d_date < CURRENT_DATE
                )
                SELECT 
                    lower(a.vc_market) || a.vc_symbol_code as full_symbol, 
                    to_date(to_char(coalesce(s.d_max_date, to_date(a.vc_list_date, 'yyyy-mm-dd')), 'yyyy-mm-dd'), 'yyyy-mm-dd') dataz
                FROM stock.stock_list_a a
                LEFT JOIN stock.stock_sync_status s ON a.vc_symbol_code = s.vc_symbol
                -- 2. 关联获取到的上一个交易日
                CROSS JOIN last_trade_day ltd
                WHERE 
                    s.d_last_sync_time IS NULL 
                    -- 3. 判断逻辑：最后同步日期 小于 上一个交易日
                    OR s.d_max_date < ltd.last_day
                ORDER BY a.vc_symbol_code asc
               """)

    with dbUtil.postgre_engine.connect() as conn:
        stocks = conn.execute(sql).fetchall()

    print(f">>> 待同步股票数量: {len(stocks)}")

    count = len(stocks)
    fail_streak = 0
    for symbol, list_date  in stocks:
        if str(list_date) > yesterday: continue

        success = sync_single_stock(symbol, str(list_date), yesterday)

        if success:
            count = count-1
            print(f">>> 待同步股票数量: {count}")
            fail_streak = 0
            time.sleep(0.1)  # 频率控制
        else:
            fail_streak += 1
            print(f"  [Alert] {symbol} 全接口同步失败")

        # 熔断机制：如果所有接口都挂了，且连续 5 只股票都同步失败
        if fail_streak >= 5:
            print("!!! 连续 5 只股票全接口失败，可能是网络问题，程序终止 !!!")
            break


if __name__ == "__main__":
    batch_update_history()