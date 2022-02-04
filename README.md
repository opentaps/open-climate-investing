# open-climate-investing

This project's mission is to make climate investing actionable.  It includes both open source software and a free book to help you identify relative value trades, optimize portfolios, and structure benchmarks for climate aligned investing.

## The Software

The software is a multi-factor equity returns model which adds a climate factor, or Brown Minus Green, to the popular Fama French and Carhart models.  This additional Brown Minus Green (BMG) return factor could be used for a variety of climate investing applications, including:
- Calculate the market-implied carbon risk of a stock, investment portfolio, mutual fund, or bond based on historical returns
- Determine the market reaction to the climate policies of a company
- Optimize a portfolio to minimize carbon risk subject to other parameters, such as index tracking or growth-value-sector investment strategies.

### Setting It Up

Install the required python modules (use `pip3` instead of `pip` according to your python installation):
```
pip install -r requirements.txt
```

Initialize the Database using:
```
python3 scripts/setup_db.py -R -d
```

### Trying It Out

Let's get the historical stock prices and returns of the MSCI World Index and its constituent sectors:
```
python scripts/get_stocks.py -f data/msci_etf_sector_mapping.csv 
python scripts/get_stocks.py -f data/msci_constituent_details.csv
```

Now let's calculate the risk factor loadings for these stocks using 60 months of monthly data at a time:
```
python scripts/get_regressions.py -d -f data/msci_etf_sector_mapping.csv -s 2010-01-01 -e 2021-01-31 --frequency MONTHLY -n DEFAULT -i 60 -b
python scripts/get_regressions.py -d -f data/msci_constituent_details.csv -s 2010-01-01 -e 2021-01-31 --frequency MONTHLY -n DEFAULT -i 60 -b
``` 

Next, let's create a daily version of the BMG climate risk series based on the difference between the stocks XOP (brown) and SMOG (green):

```
python scripts/bmg_series.py -n XOP-SMOG -b XOP -g SMOG -s 2018-01-01 -e 2022-02-01 --frequency DAILY
```

Finally, let's calculate the risk factor loadings for stocks using 2 years of daily data.  This will take a long time:
```
python3 scripts/get_regressions.py -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 -e 2021-01-31 --frequency DAILY -i 730 -n XOP-SMOG -b
python3 scripts/get_regressions.py -d -f data/msci_constituent_details.csv -s 2018-01-01 -e 2021-01-31 --frequency DAILY -i 703 -n XOP-SMOG -b
```

### Viewing the Results

Follow directions from the [ui README page](ui/README.md) to look at your results.

## The Book

The included [free book on climate investing](book/README.md) explains both climate investing concepts and how to use this project.  You can also [read it online at gitbook](https://app.gitbook.com/@opentaps/s/open-climate-investing/v/main/book).

## Project Files

- [scripts/](scripts/README.md) contains the python scripts used to run the models.
- [ui/](ui/README.md) contains the user interface.
- [data/](data/README.md) contains the data files for the models and a list of their sources.
- [R/](R/README.md) contains R scripts which were used to develop the models. 
- [book/](book/README.md) is the included book on climate investing.

## References
- [Constructing and Validating Climate Risk Factors from ESG Data: an Empirical Comparison](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3967613)
- [Carbon Risk Management (CARIMA) Manual](https://assets.uni-augsburg.de/media/filer_public/ad/69/ad6906c0-cad0-493d-ba3d-1ec7fee5fb72/carima_manual_english.pdf)
- [A Practitioner's Guide to Factor Models](https://www.cfainstitute.org/en/research/foundation/1994/a-practitioners-guide-to-factor-models)
- [The Barra US Equity Model (USE4)](http://cslt.riit.tsinghua.edu.cn/mediawiki/images/4/47/MSCI-USE4-201109.pdf)
- [Network for Greening the Financial System, Case Studies of Environmental Risk Analysis Methodologies](https://www.ngfs.net/sites/default/files/medias/documents/case_studies_of_environmental_risk_analysis_methodologies.pdf)
