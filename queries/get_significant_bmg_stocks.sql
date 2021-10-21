select SS.thru_date, S.ticker, S.name, S.sector, SS.bmg, SS.bmg_t_stat 
from stock_stats as SS join stocks as S on S.ticker = SS.ticker 
where SS.thru_date > '2018-12-01'
and SS.bmg_p_gt_abs_t < 0.05
order by S.sector, bmg
