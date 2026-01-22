from sqlalchemy import Table, Column, String, Date, Numeric, DateTime, MetaData
import datetime

metadata = MetaData()

stock_indicator = Table(
    'stock_indicator', metadata,
    # 联合主键
    Column('vc_symbol', String(20), primary_key=True, comment='股票代码'),
    Column('dt_trade', Date, primary_key=True, comment='交易日期'),

    # 估值核心三剑客：PE, PB, DV
    Column('n_pe', Numeric(18, 4), comment='市盈率(静态)'),
    Column('n_pe_ttm', Numeric(18, 4), comment='市盈率(TTM)'),
    Column('n_pb', Numeric(18, 4), comment='市净率'),

    # 营收指标
    Column('n_ps', Numeric(18, 4), comment='市销率(静态)'),
    Column('n_ps_ttm', Numeric(18, 4), comment='市销率(TTM)'),

    # 价值投资最爱
    Column('n_dv_ratio', Numeric(18, 4), comment='股息率(%)'),
    Column('n_total_mv', Numeric(20, 4), comment='总市值(万元)'),

    # 系统字段
    Column('vc_create_date', DateTime, default=datetime.datetime.now, comment='创建时间'),
    schema='stock'
)