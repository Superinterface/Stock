import datetime
import pandas as pd
import akshare as ak
from sqlalchemy import insert, text
import db.DBUtil as dbUtil
import table_model.StockIndicator as indicator


def sync_daily_indicator_snapshot():
    """获取全市场今日估值指标快照并存入数据库"""
    print(f"--- 开启每日估值指标同步: {datetime.date.today()} ---")

    try:
        # 1. 获取全市场快照 (symbol="all" 是目前最稳定的)
        df = ak.stock_a_lg_indicator(symbol="all")

        if df.empty:
            print("未能获取到今日指标数据")
            return

        # 2. 格式化数据
        df = df.rename(columns={
            "代码": "vc_symbol",
            "市盈率": "n_pe",
            "市盈率TTM": "n_pe_ttm",
            "市净率": "n_pb",
            "股息率": "n_dv_ratio",
            "总市值": "n_total_mv"
        })

        # 统一日期 (dt_trade)
        df['dt_trade'] = datetime.date.today()
        df['vc_create_date'] = datetime.datetime.now()

        # 选取我们需要的字段
        final_df = df[
            ['vc_symbol', 'dt_trade', 'n_pe', 'n_pe_ttm', 'n_pb', 'n_dv_ratio', 'n_total_mv', 'vc_create_date']]

        # 3. 落地数据库 (PostgreSQL UPSERT 逻辑)
        # 这里的 text 语法处理了重复写入的问题
        with dbUtil.postgre_engine.connect() as conn:
            with conn.begin():
                # 先清除今天可能已经存在的旧数据（防止重复跑报错）
                conn.execute(text("DELETE FROM stock_indicator WHERE dt_trade = :d"), {"d": datetime.date.today()})
                # 批量插入
                conn.execute(insert(indicator.stock_indicator), final_df.to_dict(orient="records"))

        print(f"成功同步 {len(final_df)} 只股票的今日指标。")

    except Exception as e:
        print(f"同步失败: {e}")


if __name__ == "__main__":
    sync_daily_indicator_snapshot()