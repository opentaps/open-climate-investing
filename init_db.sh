#!/bin/sh

DB_NAME="open_climate_investing_carima"

createdb ${DB_NAME}

psql ${DB_NAME} < init_schema.sql

psql ${DB_NAME} -c 'COPY ff_factor FROM STDIN WITH (FORMAT CSV, HEADER);' < data/ff_factors.csv

# import carbon risk factor, 
psql ${DB_NAME} -c 'DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;
CREATE TABLE _import_carbon_risk_factor (
    date date,
    bmg decimal(12, 10),
	PRIMARY KEY (date)
);'

psql ${DB_NAME} -c 'COPY _import_carbon_risk_factor FROM STDIN WITH (FORMAT CSV, HEADER);' < data/carbon_risk_factor.csv
psql ${DB_NAME} -c "INSERT INTO carbon_risk_factor (date, bmg, factor_name) SELECT date, bmg, 'DEFAULT' FROM _import_carbon_risk_factor;"
psql ${DB_NAME} -c 'DROP TABLE IF EXISTS _import_carbon_risk_factor CASCADE;'


psql ${DB_NAME} -c 'COPY risk_free FROM STDIN WITH (FORMAT CSV, HEADER);' < data/risk_free.csv

# load stocks with sector and sub-sector
psql ${DB_NAME} -c 'COPY stocks FROM STDIN WITH (FORMAT CSV, HEADER);' < data/spx_sector_breakdown.csv
# manual insert for the funds
# spx
psql ${DB_NAME} -c "INSERT INTO stocks (ticker, name) VALUES ('IVV', 'iShares S&P 500');"
# msci
psql ${DB_NAME} -c "INSERT INTO stocks (ticker, name) VALUES ('XWD.TO', 'iShares MSCI World');"

# import components and weights of spx
psql ${DB_NAME} -c "DROP TABLE IF EXISTS _stock_weights CASCADE; CREATE TABLE _stock_weights (
    ticker text,
    weight DECIMAL(5,2),
    PRIMARY KEY (ticker)
);
DELETE FROM stock_components WHERE ticker = 'IVV';
COPY _stock_weights FROM STDIN WITH (FORMAT CSV, HEADER);
INSERT INTO stock_components (ticker, component_stock, percentage) SELECT
'IVV', ticker, weight FROM _stock_weights;
DROP TABLE IF EXISTS _stock_weights CASCADE;
" < data/spx_constituent_weights.csv

# import components of msci
psql ${DB_NAME} -c "DROP TABLE IF EXISTS _stock_comps CASCADE; CREATE TABLE _stock_comps (
    ticker text,
    name text,
    weight decimal(8, 5),
    market_value text,
    sector text,
    country text,
    PRIMARY KEY (ticker)
);
DELETE FROM stock_components WHERE ticker = 'XWD.TO';
COPY _stock_comps FROM STDIN WITH (FORMAT CSV, HEADER);
INSERT INTO stocks (ticker, name, sector) SELECT
ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;
INSERT INTO stock_components (ticker, component_stock, percentage, sector, country) SELECT
'XWD.TO', ticker, weight, sector, country FROM _stock_comps;
DROP TABLE IF EXISTS _stock_comps CASCADE;
" < data/msci_constituent_details.csv

# CRBN Materials
psql ${DB_NAME} -c "INSERT INTO stocks (ticker, name) VALUES ('CRBN-MAT', 'iShares ACWI Low Carbon Target ETF - Materials');"

psql ${DB_NAME} -c "DROP TABLE IF EXISTS _stock_comps CASCADE; CREATE TABLE _stock_comps (
    ticker text,
    name text,
    market_value text,
    weight decimal(8, 5),
    sector text,
    PRIMARY KEY (ticker)
);
COPY _stock_comps FROM STDIN WITH (FORMAT CSV, HEADER);
INSERT INTO stocks (ticker, name, sector) SELECT
ticker, name, sector FROM _stock_comps ON CONFLICT (ticker) DO NOTHING;
INSERT INTO stock_components (ticker, component_stock, percentage, sector) SELECT
'CRBN-MAT', ticker, weight, sector FROM _stock_comps;
DROP TABLE IF EXISTS _stock_comps CASCADE;
" < data/crbn_materials_constituent_details.csv

# Clean Up Data
psql ${DB_NAME} -c "delete from stock_data where return > 1";

