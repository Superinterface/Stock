from sqlalchemy import Column, String, Date, DateTime, Table, MetaData

metadata = MetaData()

stock_sync_status = Table(
    'stock_sync_status', metadata,
    Column('vc_symbol', String(20), primary_key=True),  # 股票代码
    Column('d_min_date', Date),                        # 已存数据的最小日期
    Column('d_max_date', Date),                        # 已存数据的最大日期
    Column('d_last_sync_time', DateTime),              # 最近一次成功同步的时间
    schema='stock'
)