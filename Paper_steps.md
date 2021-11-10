# Steps to Replicate the Paper's Results

These are steps to replicate the paper "Comparison of Equity Risk Factors Constructed from ESG Data".  Please also see the videos:
- [Replicating Paper Results - Introduction and R Scripts](https://youtu.be/Dr3G14ogceU)
- [Replicating Paper Results with Python Scripts - 1](https://youtu.be/W0D8f0CqlPM)
- [Replicating Paper Results with Python Scripts - 2](https://youtu.be/YA0S69_1u0o)

The results for comparison are in two Google spreadsheets: [Carbon Loadings Results - CARIMA](https://docs.google.com/spreadsheets/d/1JJ8pGqze3TcXxYbPcai_1nOOckha8XLYoLk8vk4Y7vo/edit?usp=sharing) and [Carbon Loadings Results - Alternates](https://docs.google.com/spreadsheets/d/12NXsB2aR2w4JhA9VtjQXbDwSiTivkWMRbfbpoHxz1SY/edit?usp=sharing)

## R Scripts

### Correlation matrix

Run `R/correlation_script.R`, changing `carbon_data` to your BMG factors file.  Get the `corr_matrix` result to compare with the Correlations and the `fit` summary to compare with the BMG Regressed vs Other Factors result.

### Regressions

Run predictive power for data/msci_sector_returns.csv up to 5 to get sector market weighted returns
Run predictive power for data/msci_constituent_returns.csv 1-4 and 8 to get equal weighted results

## Python Scripts

Initialize your database with the steps from [README.md](README.md)  Then load the stock prices of the MSCI World index using the command

```
python get_stocks.py -f data/stock_tickers_msci_world.csv
```

You only need to do this once to populate the stock history data.

Clear out abnormal returns data:
```
delete from stock_data where return > 1
```

Then to run it for other BMG series:
- Run SQL `delete from stock_stats`
- Run SQL `delete from carbon_risk_factor`
- Reload carbon_risk_factor with command:
```
psql open_climate_investing  -c 'COPY carbon_risk_factor FROM STDIN WITH (FORMAT CSV, HEADER);' < new-bmg-series.csv
```

Check that the carbon risk factor you loaded is the same as your CSV file with SQL
```
select * from carbon_risk_factor
```

- Run all regressions
```
python get_regressions.py -f data/stock_tickers_msci_world.csv -e 2021-09-30
```

If you want to see how your regressions are doing, you can run this query:
```
select * from stock_stats order by ticker desc, thru_date desc
```

- Get the stocks with significant BMG results:

First we need to figure out the last signfiicant time period.  Choose any stock (COP will do): 
```
select max(thru_date) from stock_stats
where ticker = 'COP'
```

I got 2021-09-28 using `data/bmg_xop_smog_orthogonalized_2.csv`, so let's use `> 2021-09-01` in the queries below:
 
```
select SS.thru_date, S.ticker, S.name, S.sector, SS.bmg, SS.bmg_t_stat 
from stock_stats as SS join stocks as S on S.ticker = SS.ticker 
where SS.thru_date > '2021-09-01'
and SS.bmg_p_gt_abs_t < 0.05
order by S.sector, bmg
```
- Get a count of the stocks with significant BMG results by sector:
```
select distinct S.sector, count(SS.ticker)
from stock_stats as SS 
left outer join stocks as S on S.ticker = SS.ticker
where SS.thru_date > '2021-09-01'
and SS.bmg_p_gt_abs_t < 0.05
group by S.sector
```
Substitute '2021-09-01' for the last date of your regression results.
- Get a count of how many stocks with each sector had significant BMG results for at least half of the rolling regressions:

Now we need to figure out how many time periods there were.  Choose any stock (COP will do): 
```
select count(thru_date) from stock_stats
where ticker = 'COP'
```

This returned 81 for me using `data/bmg_xop_smog_orthogonalized_2.csv` which means there were 81 rolling regressions of 60 months each, 
ending from 2015-01-31 to 2021-09-28.

Then
```
select distinct S.sector, SS.ticker, S.name, count(SS.thru_date) as Count_Significant_Periods, 
avg(SS.bmg) as Avg_BMG, min(SS.bmg_t_stat) as min_BMG_t_stat, avg(SS.bmg_t_stat) as avg_BMG_t_stat, max(SS.bmg_t_stat) as max_BMG_t_stat
from stock_stats as SS
left outer join stocks as S on S.ticker = SS.ticker
where SS.bmg_p_gt_abs_t < 0.05
group by S.sector, SS.ticker, S.name
having count(SS.thru_date) > 40
order by S.sector
```
where 40 is half the number you got from the regression for how many ending dates.

### Fixing Missing Stock Tickers

You probably won't encounter this, but if the SQL queries from above show any stocks without name and sector, it's because the tickers in the `data/msci_constituent_details.csv` and `data/stock_tickers_msci_world.csv` didn't match.  To fix this:
- Edit  `data/msci_constituent_details.csv` and look for the ticker.  I've found there might be a different ending (.L or .AS or .SW) for the exchange.  Fix them to be the ticker in your query result.
- Create a file `data/msci_sector_breakdowns.csv` with the same fields as `data/spx_sector_breakdown.csv` from the `data/msci_constituent_details.csv` 
- Delete the stocks with SQL:
```
DROP TABLE STOCKS CASCADE;
CREATE TABLE stocks (
    ticker text,
    name text,
    sector text,
    sub_sector text,
    PRIMARY KEY (ticker)
);
```
- Reload stocks from msci_sector_breakdowns.csv:
```
psql open_climate_investing -c 'COPY stocks FROM STDIN WITH (FORMAT CSV, HEADER);' < data/msci_sector_breakdowns.csv 
```

## Construct your own BMG

It's easy and fun!  

First use `get_stocks.py` to get the historical prices of your stocks, if you don't have them already:
```
python get_stocks.py -t ACWI
python get_stocks.py -t CRBN 
```

Finally use this SQL:
```
select SD1.date, SD1.ticker, SD1.return, SD2.ticker, SD2.return, SD1.return-SD2.return as BMG
from stock_data as SD1
join stock_data as SD2 on SD1.date = SD2.date
where SD1.ticker = 'XOP' and SD1.date > '2010-01-01'
and SD2.ticker = 'SMOG'
```
and substitute `XOP` and `SMOG` with your tickers.  If the results look good, only select the date and BMG columns into a CSV file.

### Constructing the WMAT-CRBN_MAT BMG

This is a series of the SSgA SPDR ETFs Europe II plc - SPDR MSCI World Materials UCITS ETF. (WMAT.L) as the Brown stocks minus the Materials sector stocks of the iShares MSCI ACWI Low Carbon Target ETF (CRBN) as the Green stocks.

Get the stock returns of the CRBN Materials sector
```
python3 get_stocks.py -f data/stock_tickers_crbn_materials.csv 
```

Run the final part of `init_db.sh` under "CRBN Materials"

Get the stock returns of WMAT.L
```
python3 get_stocks.py -t WMAT.L
```

Again, clear out the abnormal returns:
```
delete from stock_data where return > 1
```

Get the difference as save as a CSV file `data/bmg_wmat_crbn_mat.csv`:
```
select SD1.date, SD1.return - SD2.return
from stock_data as SD1
join stock_data as SD2 on SD1.date = SD2.date
join carbon_risk_factor as CR on SD1.date = CR.date
where SD1.ticker = 'WMAT.L' and SD1.date > '2010-01-01'
and SD2.ticker = 'CRBN-MAT'
```


