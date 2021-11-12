--
-- This gets multiple stocks and the BMG factor from the same time period
--

select SD1.date, SD1.ticker, SD1.return, SD2.ticker, SD2.return, 
SD3.ticker, SD3.return, SD4.ticker, SD4.return, SD5.ticker, SD5.return,
CR.bmg
from stock_data as SD1
join stock_data as SD2 on SD1.date = SD2.date
join stock_data as SD3 on SD1.date = SD3.date
join stock_data as SD4 on SD1.date = SD4.date
join stock_data as SD5 on SD1.date = SD5.date
join carbon_risk_factor as CR on SD1.date = CR.date
where SD1.ticker = 'XOM' and SD1.date > '2010-01-01'
and SD2.ticker = 'CVX'
and SD3.ticker = 'SLB'
and SD4.ticker = 'PXD'
and SD5.ticker = 'VWS.CO'
