#!/bin/bash
source venv/bin/activate
CONCURRENCY="16"
FACTOR="DEFAULT"

echo "-- Updating msci_etf_sector_mapping stocks ..."
python scripts/get_stocks.py -c $CONCURRENCY -u -f data/msci_etf_sector_mapping.csv 
echo "-- Updating msci_constituent_details stocks ..."
python scripts/get_stocks.py -c $CONCURRENCY -u -f data/msci_constituent_details.csv

echo "-- Updating XOP-SMOG monthly ..."
python scripts/bmg_series.py -n ${FACTOR} -b XOP -g SMOG -s 2010-01-01 --frequency MONTHLY
echo "-- Updating XOP-SMOG daily ..."
python scripts/bmg_series.py -n ${FACTOR} -b XOP -g SMOG -s 2018-01-01 --frequency DAILY

echo "-- Updating msci_etf_sector_mapping 730 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 730 -n ${FACTOR} -b
echo "-- Updating msci_constituent_details 730 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 730 -n ${FACTOR} -b

echo "-- Updating msci_etf_sector_mapping 365 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 365 -n ${FACTOR} -b
echo "-- Updating msci_constituent_details 365 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 365 -n ${FACTOR} -b

echo "-- Updating msci_etf_sector_mapping 180 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 180 -n ${FACTOR} -b
echo "-- Updating msci_constituent_details 180 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 180 -n ${FACTOR} -b

echo "-- Updating msci_etf_sector_mapping 90 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_etf_sector_mapping.csv -s 2018-01-01 --frequency DAILY -i 90 -n ${FACTOR} -b
echo "-- Updating msci_constituent_details 90 days regressions ..."
python scripts/get_regressions.py -c $CONCURRENCY -u -d -f data/msci_constituent_details.csv -s 2018-01-01 --frequency DAILY -i 90 -n ${FACTOR} -b

