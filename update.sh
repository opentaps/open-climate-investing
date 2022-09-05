#!/bin/bash
source venv/bin/activate

python scripts/get_stocks.py -u -f data/msci_etf_sector_mapping.csv 
python scripts/get_stocks.py -u -f data/msci_constituent_details.csv
python scripts/get_regressions.py -u -d -f data/msci_etf_sector_mapping.csv -s 2010-01-01 --frequency MONTHLY -n DEFAULT -i 60 -b
python scripts/get_regressions.py -u -d -f data/msci_constituent_details.csv -s 2010-01-01 --frequency MONTHLY -n DEFAULT -i 60 -b

python scripts/bmg_series.py -n XOP-SMOG -b XOP -g SMOG -s 2010-01-01 --frequency MONTHLY
python scripts/bmg_series.py -n XOP-SMOG -b XOP -g SMOG -s 2018-01-01 --frequency DAILY

python scripts/get_regressions.py -u -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 730 -n XOP-SMOG -b
python scripts/get_regressions.py -u -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 730 -n XOP-SMOG -b

