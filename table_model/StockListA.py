import datetime

import db.DBUtil as dbUtil
from sqlalchemy import Date, Table, Column, Float, DateTime, String

stock_list_a = Table(
    "stock_list_a",
    dbUtil.postgre_metadata,
    Column("vc_symbol_code", String),
    Column("vc_symbol_name", String),
    Column("vc_symbol_full_name", String),
    Column("vc_market", String),
    Column("vc_board", String),
    Column("vc_industry", String),
    Column("vc_area", String),
    Column("vc_list_date", String),
    Column("n_total_shares", Float),
    Column("n_float_shares", Float),
    Column("vc_report_date", String),
    Column("vc_status", String),
    Column("vc_data_source", String),
    Column("vc_create_date", String),
    Column("vc_updated_time", String),
    schema='stock'
)