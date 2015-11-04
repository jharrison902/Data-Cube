#!/bin/bash

#===============================================================================
# Copyright 2015 Geoscience Australia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

# Bash script to generate and submit multiple PBS jobs each cataloguing a single
# month of NBAR files. Calls dbupdater.py

#PBS -P v10
#PBS -q normal
#PBS -l walltime=08:00:00,mem=4096MB,ncpus=1
#PBS -l wd
#@#PBS -m e
#PBS -M alex.ip@ga.gov.au

rm -rf /g/data/v10/tmp/dbupdater/g_data_v10_NBAR_*

for year in 2012 2011 2010 2009 2008 2007 2006 2005 2004 2003 2002 2001 2000
do
  for month in 12 11 10 09 08 07 06 05 04 03 02 01
  do
    cat dbupdater | sed s/\$@/--debug\ --source=\\/g\\/data\\/v10\\/NBAR\\/${year}-${month}\ --purge/g > nbar_updater_${year}-${month}
    chmod 770  nbar_updater_${year}-${month}
    qsub  nbar_updater_${year}-${month}

  done
done
