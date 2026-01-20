CREATE TABLE stock.stock_list_a (
	vc_symbol_code varchar(64) NULL,
	vc_symbol_name varchar(128) NULL,
	vc_symbol_full_name varchar(512) NULL,
	vc_market varchar(8) NULL,
	vc_board varchar(16) NULL,
	vc_industry varchar(32) NULL,
	vc_area varchar(32) NULL,
	vc_list_date varchar(32) NULL,
	n_total_shares numeric NULL,
	n_float_shares numeric NULL,
	vc_report_date varchar(64) NULL,
	vc_status varchar(16) NULL,
	vc_data_source varchar(64) NULL,
	vc_create_date varchar(64) NULL,
	vc_updated_time varchar(64) NULL
);