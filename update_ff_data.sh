#!/bin/bash

source venv/bin/activate
cd data || exit 0

rm Developed*CSV.zip
wget https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_3_Factors_CSV.zip
wget https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_3_Factors_Daily_CSV.zip
wget https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_Mom_Factor_CSV.zip
wget https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Developed_Mom_Factor_Daily_CSV.zip
unzip -o Developed_3_Factors_CSV.zip 
unzip -o Developed_3_Factors_Daily_CSV.zip 
unzip -o Developed_Mom_Factor_CSV.zip 
unzip -o Developed_Mom_Factor_Daily_CSV.zip 
rm Developed*CSV.zip

cd ..

python scripts/setup_db.py --update_data

