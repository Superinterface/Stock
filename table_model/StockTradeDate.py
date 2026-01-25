from sqlalchemy import Column, String, Date, DateTime, Table, MetaData, Integer

metadata = MetaData()

stock_trade_date = Table(
    'stock_trade_date', metadata,
    Column('d_date', Date, primary_key=True), # 日期
    Column('vc_is_trade', Integer),                 # 是否是交易日
    schema='stock'
)