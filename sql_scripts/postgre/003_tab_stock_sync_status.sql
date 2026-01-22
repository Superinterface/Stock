CREATE TABLE stock_sync_status (
    vc_symbol VARCHAR(20) PRIMARY KEY, -- 股票代码（主键）
    d_min_date DATE,                    -- 数据库中已有的最早行情日期
    d_max_date DATE,                    -- 数据库中已有的最晚行情日期
    d_last_sync_time TIMESTAMP          -- 最后一次成功执行抓取的时间
);

-- 建议给最后同步时间加一个索引，方便增量更新时快速筛选
CREATE INDEX idx_stock_sync_last_time ON stock_sync_status(d_last_sync_time);

comment on table stock_sync_status is '股票历史行情同步状态';

comment on column stock_sync_status.vc_symbol is '股票代码';
comment on column stock_sync_status.d_min_date is '最早行情日期';
comment on column stock_sync_status.d_max_date is '最晚行情日期';
comment on column stock_sync_status.d_last_sync_time is '最后一次成功执行抓取的时间';