DROP TABLE IF EXISTS carbon_risk_factor CASCADE;

CREATE TABLE carbon_risk_factor (
    date date,
    frequency text,
    factor_name text DEFAULT 'DEFAULT',
    bmg decimal(12, 10),
    PRIMARY KEY (date, frequency, factor_name)
);

DROP TABLE IF EXISTS ff_factor CASCADE;

CREATE TABLE ff_factor (
    date date,
    frequency text,
    mkt_rf decimal(8, 5),
    smb decimal(8, 5),
    hml decimal(8, 5),
    wml decimal(8, 5),
    PRIMARY KEY (date, frequency)
);

DROP TABLE IF EXISTS risk_free CASCADE;

CREATE TABLE risk_free (
    date date,
    frequency text,
    Rf decimal(8, 5),
    PRIMARY KEY (date, frequency)
);

DROP TABLE IF EXISTS bond_factor CASCADE;

CREATE TABLE bond_factor (
    date date,
    frequency text,
    rate decimal(5, 3),
    curve decimal(5, 3),
    hi_yield_spread decimal(5, 3),
    bbb_spread decimal(5, 3),
    rate_chg decimal(5, 3),
    curve_chg decimal(5, 3),
    hi_yield_spread_chg decimal(5, 3),
    bbb_spread_chg decimal(5, 3),
    PRIMARY KEY (date, frequency)
);


DROP TABLE IF EXISTS additional_factors CASCADE;

CREATE TABLE additional_factors (
    date date,
    frequency text,
    factor_name text,
    factor_value decimal(8, 5),
    PRIMARY KEY (date, frequency, factor_name)
);


DROP TABLE IF EXISTS stocks CASCADE;
CREATE TABLE stocks (
    ticker text,
    name text,
    sector text,
    sub_sector text,
    ebitda bigint,
    enterprise_value bigint,
    enterprise_to_ebitda decimal(14, 3),
    price_to_book decimal(16, 6),
    total_cash bigint,
    total_debt bigint,
    shares_outstanding bigint,
    PRIMARY KEY (ticker)
);


DROP TABLE IF EXISTS stock_components CASCADE;
CREATE TABLE stock_components (
    ticker text,
    component_stock text REFERENCES stocks (ticker),
    percentage decimal(8, 5),
    sector varchar(50),
    sub_sector varchar(50),
    country varchar(10),
    PRIMARY KEY (ticker, component_stock)
);


DROP TABLE IF EXISTS stock_data CASCADE;
CREATE TABLE stock_data (
    ticker text,
    frequency text,
    date date,
    close decimal(40, 10),
    return decimal(20, 10),
    PRIMARY KEY (ticker, frequency, date)
);


DROP TABLE IF EXISTS stock_stats CASCADE;
CREATE TABLE stock_stats (
    ticker text,
    frequency text,
    bmg_factor_name text,
    from_date date,
    thru_date date,
    data_from_date date,
    data_thru_date date,
    interval integer,
    constant decimal(12, 5),
    constant_std_error decimal(12, 5),
    constant_t_stat decimal(12, 5),
    constant_p_gt_abs_t decimal(12, 5),
    bmg decimal(12, 5),
    bmg_std_error decimal(12, 5),
    bmg_t_stat decimal(12, 5),
    bmg_p_gt_abs_t decimal(12, 5),
    mkt_rf decimal(12, 5),
    mkt_rf_std_error decimal(12, 5),
    mkt_rf_t_stat decimal(12, 5),
    mkt_rf_p_gt_abs_t decimal(12, 5),
    smb decimal(12, 5),
    smb_std_error decimal(12, 5),
    smb_t_stat decimal(12, 5),
    smb_p_gt_abs_t decimal(12, 5),
    hml decimal(12, 5),
    hml_std_error decimal(12, 5),
    hml_t_stat decimal(12, 5),
    hml_p_gt_abs_t decimal(12, 5),
    wml decimal(12, 5),
    wml_std_error decimal(12, 5),
    wml_t_stat decimal(12, 5),
    wml_p_gt_abs_t decimal(12, 5),
    jarque_bera decimal(12, 5),
    jarque_bera_p_gt_abs_t decimal(12, 5),
    breusch_pagan decimal(12, 5),
    breusch_pagan_p_gt_abs_t decimal(12, 5),
    durbin_watson decimal(12, 5),
    r_squared decimal(12, 5),
    PRIMARY KEY (ticker, frequency, bmg_factor_name, from_date, thru_date)
);

CREATE INDEX factor_names ON stock_stats (bmg_factor_name);
CREATE INDEX frequencies ON stock_stats (frequency);
CREATE INDEX intervals ON stock_stats (interval);
CREATE INDEX frequencies_intervals ON stock_stats (frequency, interval);
CREATE INDEX series_names ON stock_stats (ticker, bmg_factor_name, interval);
CREATE INDEX count_all_stats ON stock_stats (bmg_factor_name, frequency);

DROP MATERIALIZED VIEW IF EXISTS stock_and_stats;
DROP VIEW IF EXISTS stock_and_stats;
CREATE MATERIALIZED VIEW stock_and_stats AS
select
s.* ,
ss.frequency,
ss.interval,
ss.bmg_factor_name,
ss.from_date,
x.thru_date,
ss.data_from_date,
ss.data_thru_date,
ss.constant,
ss.constant_std_error,
ss.constant_t_stat,
ss.constant_p_gt_abs_t,
ss.bmg,
ss.bmg_std_error,
ss.bmg_t_stat,
ss.bmg_p_gt_abs_t,
ss.mkt_rf,
ss.mkt_rf_std_error,
ss.mkt_rf_t_stat,
ss.mkt_rf_p_gt_abs_t,
ss.smb,
ss.smb_std_error,
ss.smb_t_stat,
ss.smb_p_gt_abs_t,
ss.hml,
ss.hml_std_error,
ss.hml_t_stat,
ss.hml_p_gt_abs_t,
ss.wml,
ss.wml_std_error,
ss.wml_t_stat,
ss.wml_p_gt_abs_t,
ss.jarque_bera,
ss.jarque_bera_p_gt_abs_t,
ss.breusch_pagan,
ss.breusch_pagan_p_gt_abs_t,
ss.durbin_watson,
ss.r_squared
from stocks s
left join (
select
    ticker,
    frequency,
    interval,
    bmg_factor_name,
    max(thru_date) as thru_date
from stock_stats ss
group by
    ticker, frequency, interval, bmg_factor_name
) x on x.ticker = s.ticker
left join stock_stats ss on ss.ticker = s.ticker and ss.frequency = x.frequency and ss.interval = x.interval and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date;

-- query this parent_ticker to get data of the components of that stock
DROP MATERIALIZED VIEW IF EXISTS stock_component_and_stats;
DROP VIEW IF EXISTS stock_component_and_stats;
CREATE MATERIALIZED VIEW stock_component_and_stats AS
select
s.*,
sc.ticker as parent_ticker,
sc.percentage,
ss.frequency,
ss.interval,
ss.bmg_factor_name,
ss.from_date,
x.thru_date,
ss.data_from_date,
ss.data_thru_date,
ss.constant,
ss.constant_std_error,
ss.constant_t_stat,
ss.constant_p_gt_abs_t,
ss.bmg,
ss.bmg_std_error,
ss.bmg_t_stat,
ss.bmg_p_gt_abs_t,
ss.mkt_rf,
ss.mkt_rf_std_error,
ss.mkt_rf_t_stat,
ss.mkt_rf_p_gt_abs_t,
ss.smb,
ss.smb_std_error,
ss.smb_t_stat,
ss.smb_p_gt_abs_t,
ss.hml,
ss.hml_std_error,
ss.hml_t_stat,
ss.hml_p_gt_abs_t,
ss.wml,
ss.wml_std_error,
ss.wml_t_stat,
ss.wml_p_gt_abs_t,
ss.jarque_bera,
ss.jarque_bera_p_gt_abs_t,
ss.breusch_pagan,
ss.breusch_pagan_p_gt_abs_t,
ss.durbin_watson,
ss.r_squared
from stock_components sc
left join stocks s on s.ticker = sc.component_stock
left join (
select
    ticker,
    frequency,
    interval,
    bmg_factor_name,
    max(thru_date) as thru_date
from stock_stats ss
group by
    ticker, frequency, interval, bmg_factor_name
) x on x.ticker = s.ticker
left join stock_stats ss on ss.ticker = s.ticker and ss.frequency = x.frequency and ss.interval = x.interval and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date;


-- query this component_stock to get data of the parent stocks
DROP MATERIALIZED VIEW IF EXISTS stock_parent_and_stats;
DROP VIEW IF EXISTS stock_parent_and_stats;
CREATE MATERIALIZED VIEW stock_parent_and_stats AS
select
s.*,
sc.component_stock,
sc.percentage,
ss.frequency,
ss.interval,
ss.bmg_factor_name,
ss.from_date,
x.thru_date,
ss.data_from_date,
ss.data_thru_date,
ss.constant,
ss.constant_std_error,
ss.constant_t_stat,
ss.constant_p_gt_abs_t,
ss.bmg,
ss.bmg_std_error,
ss.bmg_t_stat,
ss.bmg_p_gt_abs_t,
ss.mkt_rf,
ss.mkt_rf_std_error,
ss.mkt_rf_t_stat,
ss.mkt_rf_p_gt_abs_t,
ss.smb,
ss.smb_std_error,
ss.smb_t_stat,
ss.smb_p_gt_abs_t,
ss.hml,
ss.hml_std_error,
ss.hml_t_stat,
ss.hml_p_gt_abs_t,
ss.wml,
ss.wml_std_error,
ss.wml_t_stat,
ss.wml_p_gt_abs_t,
ss.jarque_bera,
ss.jarque_bera_p_gt_abs_t,
ss.breusch_pagan,
ss.breusch_pagan_p_gt_abs_t,
ss.durbin_watson,
ss.r_squared
from stock_components sc
left join stocks s on s.ticker = sc.ticker
left join (
select
    ticker,
    bmg_factor_name,
    frequency,
    interval,
    max(thru_date) as thru_date
from stock_stats ss
group by
    ticker, frequency, interval, bmg_factor_name
) x on x.ticker = s.ticker
left join stock_stats ss on ss.ticker = s.ticker and ss.frequency = x.frequency and ss.interval = x.interval and ss.bmg_factor_name = x.bmg_factor_name and ss.thru_date = x.thru_date;

