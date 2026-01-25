
import db.DBUtil as dbUtil
from sqlalchemy import Date, Table, Column, Float, DateTime, String

stock_history = Table(
    "stock_history",
    dbUtil.postgre_metadata,
    Column("vc_date", String),    #交易日期
    Column("vc_symbol", String),        #个券代码
    Column("n_open_price", String),     #开盘价(元)
    Column("n_close_price", String),    #收盘价(元)
    Column("n_hight_price", String),    #最高价(元)
    Column("n_low_price", String),      #最低价(元)
    Column("n_trading_num", String),    #成交量(手)
    Column("n_trading_amount", String), #成交额(元)
    Column("n_amplitude", Float),       #振幅(%)
    Column("n_price_range", Float),     #涨跌幅(%)
    Column("n_price_change", String),   #涨跌额(元)
    Column("n_change_hands", String),   #换手率(%)
    Column("vc_data_source", String),   #数据来源
    Column("d_create_date", DateTime),    #数据创建时间
    schema='stock'
)