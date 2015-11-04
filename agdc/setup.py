#!/usr/bin/env python

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

from distutils.core import setup

version = '1.1.1'

setup(name='agdc',
      version = version,
      packages = [
                  'agdc',
                  'agdc.abstract_ingester',
                  'agdc.landsat_ingester',
		  'agdc.ls5_ingester',
                  'agdc.ls7_ingester',
                  'agdc.ls8_ingester'
                  ],
      package_data = {
                      'agdc': ['agdc_default.conf']
                      },
      scripts = ['bin/stacker.sh',
                 'bin/landsat_ingester.sh',
                 'bin/generic_ingester.sh',
		 'bin/ls5_ingester.sh',
                 'bin/ls8_ingester.sh',
                 'bin/modis_ingester.sh',
                 'bin/bulk_submit_interactive.sh',
                 'bin/bulk_submit_pbs.sh'
                 ],
      requires = [
                  'EOtools',
                  'psycopg2',
                  'gdal',
                  'numexpr',
                  'scipy',
                  'dateutil',
                  'pytz'
                  ],
      url = 'https://github.com/GeoscienceAustralia/ga-datacube',
      author = 'Alex Ip, Matthew Hoyles, Matthew Hardy',
      maintainer = 'Alex Ip, Geoscience Australia',
      maintainer_email = 'alex.ip@ga.gov.au',
      description = 'Australian Geoscience Data Cube (AGDC)',
      long_description = 'Australian Geoscience Data Cube (AGDC). Original Python code developed during the Unlocking the Landsat Archive. (ULA) Project, 2013',
      license = 'BSD 3'
     )
