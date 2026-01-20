#A股票列表
import datetime
from sqlalchemy import insert, delete
from sqlalchemy.orm import sessionmaker

import akshare as ak

import db.DBUtil as dbUtil
import table_model.StockListA as stock_list
import pandas as pd

# 设置显示所有列
pd.set_option('display.max_columns', None)

# 创建Session类对象
#Session = sessionmaker(bind=dbUtil.oracle_engine)
# 创建Session类实例
#session = Session()

''' 上交所股票列表获取'''
#获取上交所A股票列表
sh = ak.stock_info_sh_name_code(symbol="主板A股")

sh.rename(columns={"证券代码": "vc_symbol_code","证券简称": "vc_symbol_name","证券全称": "vc_symbol_full_name","上市日期": "vc_list_date",}, inplace=True)

sh = sh.drop(columns=['公司简称','公司全称'])

sh['vc_market'] = 'SH'
sh['vc_board'] = ''
sh['vc_industry'] = ''
sh['vc_area'] = ''
sh['n_total_shares'] = 0
sh['n_float_shares'] = 0
sh['vc_report_date'] = ''
sh['vc_status'] = '正常上市'
sh['vc_data_source'] = 'stock_info_sh_name_code'
sh['vc_create_date'] = datetime.datetime.now()
sh['vc_updated_time'] = datetime.datetime.now()


''' 上交所股票列表落地'''
# 先删除日期对应的旧数据，再更新
#session.query(stock_list.stock_list_a).filter(stock_list.stock_list_a.columns.VC_SYMBOL_CODE.in_(sh['VC_SYMBOL_CODE'])).delete(synchronize_session=False)
#session.commit()

delStmt = delete(stock_list.stock_list_a).where(stock_list.stock_list_a.c.vc_market == 'SH')
with dbUtil.postgre_engine.connect() as conn:
    conn.execute(delStmt)
    conn.commit()

# 插入数据
stmt = insert(stock_list.stock_list_a)

with dbUtil.postgre_engine.connect() as conn:
    conn.execute(stmt, sh.to_dict(orient="records"))
    conn.commit()



''' 深交所股票列表获取 '''
sz = ak.stock_info_sz_name_code(symbol="A股列表")
sz.rename(
    columns={
        "A股代码": "vc_symbol_code",
        "A股简称": "vc_symbol_name",
        "A股上市日期": "vc_list_date",
        "板块": "vc_board",
        "A股总股本": "n_total_shares",
        "A股流通股本": "n_float_shares",
        "所属行业": "vc_industry",
    }, inplace=True)

sz['vc_symbol_full_name'] = sz['vc_symbol_name']
sz['vc_market'] = 'SZ'
sz['vc_area'] = ''
sz['vc_report_date'] = ''
sz['vc_status'] = '正常上市'
sz['vc_data_source'] = 'stock_info_sz_name_code'
sz['vc_create_date'] = datetime.datetime.now()
sz['vc_updated_time'] = datetime.datetime.now()

sz['vc_list_date'] = pd.to_datetime(sz['vc_list_date']).dt.date
sz['n_total_shares'] = sz['n_total_shares'].str.replace(',', '').astype(float)
sz['n_float_shares'] = sz['n_float_shares'].str.replace(',', '').astype(float)

''' 深交所股票列表落地 '''
# 先删除对应的旧数据，再更新
#session.query(stock_list.stock_list_a).filter(stock_list.stock_list_a.c.VC_SYMVOL_CODE.in_(sz['VC_SYMBOL_CODE'])).delete(synchronize_session=False)
#session.commit()

delStmt = delete(stock_list.stock_list_a).where(stock_list.stock_list_a.c.vc_market == 'SZ')
with dbUtil.postgre_engine.connect() as conn:
    conn.execute(delStmt)
    conn.commit()

# 插入数据
stmt = insert(stock_list.stock_list_a)

with dbUtil.postgre_engine.connect() as conn:
    conn.execute(stmt, sz.to_dict(orient="records"))
    conn.commit()


''' 北交所股票列表获取 '''
bj = ak.stock_info_bj_name_code()
bj.rename(
    columns={
        "证券代码": "vc_symbol_code",
        "证券简称": "vc_symbol_name",
        "上市日期": "vc_list_date",
        "板块": "vc_board",
        "总股本": "n_total_shares",
        "流通股本": "n_float_shares",
        "所属行业": "vc_industry",
        "地区": "vc_area",
        "报告日期": "vc_report_date",
    }, inplace=True)

bj['vc_symbol_full_name'] = sz['vc_symbol_name']
bj['vc_market'] = 'BJ'
bj['vc_board'] = ''
bj['vc_status'] = '正常上市'
bj['vc_data_source'] = 'stock_info_sz_name_code'
bj['vc_create_date'] = datetime.datetime.now()
bj['vc_updated_time'] = datetime.datetime.now()

bj['vc_list_date'] = pd.to_datetime(bj['vc_list_date']).dt.date

delStmt = delete(stock_list.stock_list_a).where(stock_list.stock_list_a.c.vc_market == 'BJ')
with dbUtil.postgre_engine.connect() as conn:
    conn.execute(delStmt)
    conn.commit()

# 插入数据
stmt = insert(stock_list.stock_list_a)

with dbUtil.postgre_engine.connect() as conn:
    conn.execute(stmt, bj.to_dict(orient="records"))
    conn.commit()


print('== stock_list_a(A股列表) 数据落地成功 ==')