#!/bin/bash

cd $1
RSI=`ls -1 $1 | head -n 1 | grep -o '[A-Z0-9]\+\?' | head -n 1`
python /tilestore/DataCube-dist/preprocess/build_pqa_"$2".py $RSI
mkdir pqa
cp *.xml pqa/.
mv *_PQA*.tif pqa/.
rename s/sr_band/B/ *.tif
if [ "ls5" = "$2" ]; then
rename s/\.tif/0.TIF/ *.tif;
ls5_ingester.sh --source .;
ls5_ingester.sh --source ./pqa;
fi
if [ "ls7" = "$2" ]; then
rename s/\.tif/0.TIF/ *.tif;
generic_ingester.sh --source .;
generic_ingester.sh --source ./pqa;
fi
if [ "ls8" = "$2" ]; then
rename s/\.tif/.TIF/ *.tif;
ls8_ingester.sh --source .;
ls8_ingester.sh --source ./pqa;
fi
