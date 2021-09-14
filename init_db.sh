#!/bin/sh

DB_NAME="open_climate_investing"

createdb ${DB_NAME}

psql ${DB_NAME} < init_schema.sql

psql ${DB_NAME} -c 'COPY ff_factor FROM STDIN WITH (FORMAT CSV, HEADER);' < ff_factors.csv
psql ${DB_NAME} -c 'COPY carbon_risk_factor FROM STDIN WITH (FORMAT CSV, HEADER);' < carbon_risk_factor.csv
