#!/bin/bash

#################
# Datacube installer
# Requirements:
# Centos 7
# Ubuntu
#################

# Install preqs for software!
DIR="$(pwd)"
EXEC_PATH_REL="`dirname \"$0\"`"
EXEC_PATH="`( cd \"$EXEC_PATH_REL\" && pwd )`"


if [ -f /etc/redhat-release ]; then

echo "Centos not supported with this script";
else
echo "ubuntu detected";
sudo apt-get update;
sudo apt-get install -y pv environment-modules libgdal-dev gdal-bin python-gdal python-scipy python-numexpr python-numpy python-psycopg2 postgresql libpq-dev postgresql-contrib postgis postgresql-9.3-postgis-2.1 python-tz git wget;
fi

cd /tmp
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install ephem numexpr psutil datetime luigi enum34 pytest
cd ..

cd $EXEC_PATH
cd ..
pwd
ls
cd "EO_tools"
sudo python setup.py install --force
cd ..

"Installing the datacube..."
cd "agdc"
sudo mkdir /g
sudo chmod a+rwx /g

cd "database"
cd "sql"

pwd

#restore the database
echo "Restoring the database..."
sudo -u postgres psql -c "CREATE USER cube_user;"
sudo -u postgres psql -c "CREATE USER cube_admin WITH PASSWORD 'GAcube0';"
sudo -u postgres psql -c "CREATE USER jeremyhooke WITH PASSWORD 'GAcube0';"
sudo -u postgres psql -c "CREATE DATABASE datacubev1;"
sudo -u postgres psql -c "ALTER ROLE cube_user WITH SUPERUSER;"
sudo -u postgres psql -c "ALTER ROLE cube_admin WITH SUPERUSER;"
sudo -u postgres psql -c "ALTER ROLE jeremyhooke WITH SUPERUSER;"
sudo -u postgres psql -c "CREATE GROUP cube_user_group;"
sudo -u postgres psql -c "CREATE GROUP cube_admin_group;"
sudo -u postgres psql datacubev1 < v1__schema.sql
sudo -u postgres psql datacubev1 < v2__base_data.sql
sudo -u postgres psql datacubev1 < v3__additional_constraints.sql
sudo -u postgres psql datacubev1 < v4__modis.sql
sudo -u postgres psql datacubev1 < v5__wofs.sql
sudo -u postgres psql datacubev1 < v6__index.sql
sudo -u postgres psql -c "ALTER ROLE cube_user WITH PASSWORD 'GAcube0';"

cd ..
cd ..

######
# We will not encourage no authentication by setting that up by default.
######
echo "pg_hba.conf will not be configured for you! Please configure to your liking."
echo "Running install script..."
sudo python setup.py install --force
echo "Datacube installed!"
#edit the api config.
echo "Installing the datacube api..."
cd api
echo "Running install script..."
sudo python setup.py install --force
echo "Datacube api installed!"


echo "Installation complete!"
cd /
sudo mkdir tilestore
sudo chmod 777 tilestore

cd $EXEC_PATH
cd ..
pwd
sudo cp kenya_cells.txt /tilestore/kenya_cells.txt
