select SS.thru_date, S.ticker, S.name, S.sector, SS.bmg, SS.bmg_t_stat 
from stock_stats as SS join stocks as S on S.ticker = SS.ticker 
where SS.thru_date = '2022-08-31'
and SS.bmg_p_gt_abs_t < 0.05
and SS.bmg_factor_name = 'DEFAULT'
and SS.interval = 365
and SS.frequency = 'DAILY'
order by S.ticker;
