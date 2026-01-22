-- 创建股票估值及基本面指标表
CREATE TABLE stock_indicator (
    vc_symbol VARCHAR(20) NOT NULL,       -- 股票代码
    dt_trade DATE NOT NULL,               -- 交易日期
    n_pe NUMERIC(18, 4),                 -- 市盈率(静态): 当前总市值 / 上一年度净利润
    n_pe_ttm NUMERIC(18, 4),             -- 市盈率(TTM): 当前总市值 / 最近四个季度净利润之和(滚动)
    n_pb NUMERIC(18, 4),                 -- 市净率: 当前总市值 / 最近一期净资产
    n_ps NUMERIC(18, 4),                 -- 市销率(静态): 当前总市值 / 上一年度营业收入
    n_ps_ttm NUMERIC(18, 4),             -- 市销率(TTM): 当前总市值 / 最近四个季度营业收入之和
    n_dv_ratio NUMERIC(18, 4),           -- 股息率(%): 最近一年累计分红金额 / 当前总市值 * 100
    n_total_mv NUMERIC(20, 4),           -- 总市值(万元): 股票总股本 * 当前收盘价
    vc_create_date TIMESTAMP DEFAULT NOW(),-- 记录落库时间
    PRIMARY KEY (vc_symbol, dt_trade)    -- 联合主键：确保同一只股票每天只有一条指标记录
);

-- 添加表级别注释
COMMENT ON TABLE stock_indicator IS '股票每日估值及基本面指标表(来自乐咕数据)';

-- 添加字段级别详细注释
COMMENT ON COLUMN stock_indicator.vc_symbol IS '股票代码';
COMMENT ON COLUMN stock_indicator.dt_trade IS '交易日期';
COMMENT ON COLUMN stock_indicator.n_pe IS '市盈率(静态): 基于最近一个审计年度净利润计算';
COMMENT ON COLUMN stock_indicator.n_pe_ttm IS '市盈率(TTM): 基于最近四个季度累计净利润计算，更具实时性';
COMMENT ON COLUMN stock_indicator.n_pb IS '市净率: 衡量股价是否跌破资产价值，<1代表破净';
COMMENT ON COLUMN stock_indicator.n_ps IS '市销率(静态): 反映公司营收规模相对于市值的比例';
COMMENT ON COLUMN stock_indicator.n_ps_ttm IS '市销率(TTM): 滚动12个月营收计算的市销率';
COMMENT ON COLUMN stock_indicator.n_dv_ratio IS '股息率(%): 越高代表现金分红回报越高，价值投资核心指标';
COMMENT ON COLUMN stock_indicator.n_total_mv IS '总市值(万元): 衡量公司体量，大盘股 vs 小盘股的判断标准';
COMMENT ON COLUMN stock_indicator.vc_create_date IS '数据入库的时间戳';

-- 建立索引加速分析
CREATE INDEX idx_indicator_sym ON stock_indicator(vc_symbol);
CREATE INDEX idx_indicator_date ON stock_indicator(dt_trade);