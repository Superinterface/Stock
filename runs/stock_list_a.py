import datetime
import pandas as pd
import akshare as ak
from sqlalchemy import insert, delete
import db.DBUtil as dbUtil
import table_model.StockListA as stock_list


def sync_stock_list_a():
    """全量更新 A 股股票列表"""
    print("--- 正在同步股票列表 ---")
    try:
        # 1. 获取数据
        sh_df = ak.stock_info_sh_name_code(symbol="主板A股")
        sz_df = ak.stock_info_sz_name_code(symbol="A股列表")
        bj_df = ak.stock_info_bj_name_code()

        # 2. 格式统一化加工
        # 上交所
        sh_df = sh_df.rename(
            columns={"证券代码": "vc_symbol_code", "证券简称": "vc_symbol_name", "证券全称": "vc_symbol_full_name",
                     "上市日期": "vc_list_date"})
        sh_df['vc_market'] = 'SH'

        # 深交所
        sz_df = sz_df.rename(
            columns={"A股代码": "vc_symbol_code", "A股简称": "vc_symbol_name", "A股上市日期": "vc_list_date",
                     "板块": "vc_board", "A股总股本": "n_total_shares", "A股流通股本": "n_float_shares",
                     "所属行业": "vc_industry"})
        sz_df['vc_symbol_full_name'] = sz_df['vc_symbol_name']
        sz_df['vc_market'] = 'SZ'

        # 北交所
        bj_df = bj_df.rename(
            columns={"证券代码": "vc_symbol_code", "证券简称": "vc_symbol_name", "上市日期": "vc_list_date",
                     "板块": "vc_board", "总股本": "n_total_shares", "流通股本": "n_float_shares",
                     "所属行业": "vc_industry", "地区": "vc_area"})
        bj_df['vc_symbol_full_name'] = bj_df['vc_symbol_name']
        bj_df['vc_market'] = 'BJ'

        # 合并清洗
        all_stocks = pd.concat([sh_df, sz_df, bj_df], ignore_index=True)
        all_stocks['vc_status'] = '正常上市'
        all_stocks['vc_create_date'] = datetime.datetime.now()
        all_stocks['vc_updated_time'] = datetime.datetime.now()
        all_stocks['vc_list_date'] = pd.to_datetime(all_stocks['vc_list_date']).dt.strftime('%Y-%m-%d')

        # --- 重点修正部分：处理千分位逗号 ---
        num_cols = ['n_total_shares', 'n_float_shares']
        for col in num_cols:
            if col in all_stocks.columns:
                # 1. 确保是字符串类型以便使用 .str 方法
                all_stocks[col] = all_stocks[col].astype(str)
                # 2. 去掉逗号
                all_stocks[col] = all_stocks[col].str.replace(',', '', regex=False)
                # 3. 转换为浮点数（或整数），处理空值或无效值
                all_stocks[col] = pd.to_numeric(all_stocks[col], errors='coerce').fillna(0)

        # ----------------------------------
        # 3. 落地数据库 (事务处理：先删后插)
        with dbUtil.postgre_engine.connect() as conn:
            with conn.begin():
                conn.execute(delete(stock_list.stock_list_a))
                conn.execute(insert(stock_list.stock_list_a), all_stocks.to_dict(orient="records"))

        print(f"成功同步 {len(all_stocks)} 条股票列表数据")
        return True
    except Exception as e:
        print(f"列表同步异常: {e}")
        return False


if __name__ == "__main__":
    sync_stock_list_a()