-- 股票历史行情
create table stock_history(
	vc_date			varchar(16), -- 交易日期
	vc_symbol		varchar(32), -- 个券代码
	n_open_price 	numeric, -- 开盘价(元)
	n_close_price	numeric, -- 收盘价(元)
	n_hight_price	numeric, -- 最高价(元)
	n_low_price		numeric, -- 最低价(元)
	n_trading_num 	numeric, -- 成交量(手)
	n_trading_amount numeric,-- 成交额(元)
	n_amplitude		numeric, -- 振幅(%)
	n_price_range	numeric, -- 涨跌幅(%)
	n_price_change	numeric, -- 涨跌额(元)
	n_change_hands	numeric, -- 换手率(%)
	vc_data_source	varchar(32), -- 数据来源
	d_create_date	timestamp	-- 数据创建时间
);
-- 表注释
COMMENT ON TABLE stock_history IS '股票历史行情';
-- 字段注释
COMMENT ON COLUMN stock_history.vc_date IS '交易日';
COMMENT ON COLUMN stock_history.vc_symbol IS '股票代码';
COMMENT ON COLUMN stock_history.n_open_price IS '开盘价(元)';
COMMENT ON COLUMN stock_history.n_close_price IS '收盘价(元)';
COMMENT ON COLUMN stock_history.n_hight_price IS '最高价(元)';
COMMENT ON COLUMN stock_history.n_low_price IS '最低价(元)';
COMMENT ON COLUMN stock_history.n_trading_num IS '成交量(手)';
COMMENT ON COLUMN stock_history.n_trading_amount IS '成交额(元)';
COMMENT ON COLUMN stock_history.n_amplitude IS '振幅(%)';
COMMENT ON COLUMN stock_history.n_price_range IS '涨跌幅(%)';
COMMENT ON COLUMN stock_history.n_price_change IS '涨跌额(元)';
COMMENT ON COLUMN stock_history.n_change_hands IS '换手率(%)';
COMMENT ON COLUMN stock_history.vc_data_source IS '数据来源';
COMMENT ON COLUMN stock_history.d_create_date IS '数据创建时间';