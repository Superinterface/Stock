create table stock_list_a(
       vc_symbol_code      varchar2(64), -- 股票代码
       vc_symbol_name      varchar2(128),-- 股票简称
       vc_symbol_full_name varchar2(512),-- 公司全称
       vc_market           varchar2(8),  -- 交易所简称(SH/SZ/BJ)
       vc_board            varchar2(16), -- 板块(主板/科创板/创业板/等)
       vc_industry         varchar2(32), -- 所属行业
       vc_area             varchar2(32), -- 地区
       d_list_date         date,         -- 上市日期
       n_total_shares      number,       -- 总股本 (单位: 股)
       n_float_shares      number,       -- 流通股本 (单位: 股)
       d_report_date       date,         -- 数据报告日期 (适用于北交所接口)
       vc_status           varchar2(16), -- 上市状态
       vc_data_source      varchar2(64), -- 数据来源接口
       d_create_date       date,         -- 记录创建时间
       d_updated_time      date          -- 记录最后更新时间
);
comment on table stock_list_a is 'A股票列表';
COMMENT ON COLUMN stock_list_a.vc_symbol_code IS '股票代码，唯一标识';
COMMENT ON COLUMN stock_list_a.vc_symbol_name IS '股票简称';
COMMENT ON COLUMN stock_list_a.vc_symbol_full_name IS '公司全称';
COMMENT ON COLUMN stock_list_a.vc_market IS '交易所简称(SH-上交所/SZ-深交所/BJ-北交所)';
COMMENT ON COLUMN stock_list_a.vc_board IS '板块(主板/科创板/创业板/等)';
COMMENT ON COLUMN stock_list_a.vc_industry IS '所属行业';
COMMENT ON COLUMN stock_list_a.vc_area IS '地区';
COMMENT ON COLUMN stock_list_a.d_list_date IS '上市日期';
COMMENT ON COLUMN stock_list_a.n_total_shares IS '总股本，单位：股';
COMMENT ON COLUMN stock_list_a.n_float_shares IS '流通股本，单位：股';
COMMENT ON COLUMN stock_list_a.d_report_date IS '数据报告日期(适用于北交所接口)';
COMMENT ON COLUMN stock_list_a.vc_status IS '上市状态(正常上市/ST/退市等)';
COMMENT ON COLUMN stock_list_a.vc_data_source IS '数据来源接口(如:stock_info_sz_name_code)';
COMMENT ON COLUMN stock_list_a.d_create_date IS '记录创建时间';
COMMENT ON COLUMN stock_list_a.d_updated_time IS '记录最后更新时间';