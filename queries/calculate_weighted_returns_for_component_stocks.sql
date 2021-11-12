-- 
-- These queries help construct the weighted returns for a group of stocks and can be used to construct a BMG
-- If we have historical weights on in component_stock then it should be matched to the date of the returns.
--

-- query for double checking our work
select  SD.date, SD.ticker, SS.percentage, SD.return, SS.percentage*SD.return from stock_components as SS
join stock_data as SD
on SS.component_stock = SD.ticker
where SS.ticker = 'CRBN-MAT'
and SD.date = '2016-01-31'
and SD.return <> 'NaN'
order by SD.ticker

-- summing up
insert into stock_data (date, ticker, return)
select distinct SD.date, 'CRBN-MAT', sum(SS.percentage*SD.return)/sum(SS.percentage) from stock_components as SS
join stock_data as SD
on SS.component_stock = SD.ticker
where SS.ticker = 'CRBN-MAT'
and SD.return <> 'NaN' 
and SD.date > '2010-01-01'
group by SD.date
order by SD.date


