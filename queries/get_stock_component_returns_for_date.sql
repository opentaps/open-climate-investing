select S.ticker, SD.return from stocks as S 
join stock_data as SD on S.ticker = SD.ticker
join stock_components as SC on SC.component_stock = S.ticker
where sector in ('Communication', 'Communication Services')
and SD.date='2010-09-30'
and SC.ticker = 'XWD.TO'
order by S.ticker
