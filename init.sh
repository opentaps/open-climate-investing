#!/bin/bash
source venv/bin/activate
CONCURRENCY="16"
FACTOR="DEFAULT"

python scripts/setup_db.py -R -d
python scripts/get_stocks.py -c ${CONCURRENCY} -f data/msci_etf_sector_mapping.csv 
python scripts/get_stocks.py -c ${CONCURRENCY} -f data/msci_constituent_details.csv

python scripts/bmg_series.py -n ${FACTOR} -b XOP -g SMOG -s 2010-01-01 --frequency MONTHLY
python scripts/bmg_series.py -n ${FACTOR} -b XOP -g SMOG -s 2018-01-01 --frequency DAILY

python scripts/get_regressions.py -c ${CONCURRENCY} -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 730 -n ${FACTOR} -b
python scripts/get_regressions.py -c ${CONCURRENCY} -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 730 -n ${FACTOR} -b

