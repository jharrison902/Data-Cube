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

"""
    landsat_ingester.py - Ingester script for landsat datasets.
"""
from __future__ import absolute_import

import os
import sys
import datetime
import re
import logging
import argparse

from EOtools.execute import execute
from agdc.abstract_ingester import AbstractIngester
from .landsat_dataset import LandsatDataset

#
# Set up root logger
#
# Note that the logging level of the root logger will be reset to DEBUG
# if the --debug flag is set (by AbstractIngester.__init__). To recieve
# DEBUG level messages from a module do two things:
#    1) set the logging level for the module you are interested in to DEBUG,
#    2) use the --debug flag when running the script.
#

logging.basicConfig(stream=sys.stdout,
                    format='%(message)s',
                    level=logging.INFO)

#
# Set up logger (for this module).
#

LOGGER = logging.getLogger(__name__)


class LandsatIngester(AbstractIngester):
    """Ingester class for Landsat datasets."""

    @classmethod
    def arg_parser(cls):
        """Make a parser for required args."""

        # Extend the default parser
        _arg_parser = super(LandsatIngester, cls).arg_parser()

        _arg_parser.add_argument('--source', dest='source_dir',
            required=True,
            help='Source root directory containing datasets')

        follow_symlinks_help = \
            'Follow symbolic links when finding datasets to ingest'
        _arg_parser.add_argument('--followsymlinks',
                                 dest='follow_symbolic_links',
                                 default=False, action='store_const',
                                 const=True, help=follow_symlinks_help)

        return _arg_parser

    def find_datasets(self, source_dir):
        """Return a list of path to the datasets under 'source_dir'.

        Datasets are identified as a directory containing a 'scene01'
        subdirectory.

        Datasets are filtered by path, row, and date range if
        fast filtering is on (command line flag)."""

        LOGGER.info('Searching for datasets in %s', source_dir)
        if self.args.follow_symbolic_links:
            command = "find -L %s -name 'scene01' | sort" % source_dir
        else:
            command = "find %s -name 'scene01' | sort" % source_dir
        LOGGER.debug('executing "%s"', command)
        result = execute(command)
        assert not result['returncode'], \
            '"%s" failed: %s' % (command, result['stderr'])

        dataset_list = [os.path.abspath(re.sub(r'/scene01$', '', scenedir))
                        for scenedir in result['stdout'].split('\n')
                        if scenedir]

        if self.args.fast_filter:
            dataset_list = self.fast_filter_datasets(dataset_list)

        return dataset_list

    def fast_filter_datasets(self, dataset_list):
        """Filter a list of dataset paths by path/row and date range."""

        new_list = []
        for dataset_path in dataset_list:
            match = re.search(r'_(\d{3})_(\d{3})_(\d{4})(\d{2})(\d{2})$',
                              dataset_path)
            if match:
                (path, row, year, month, day) = map(int, match.groups())

                if self.filter_dataset(path,
                                       row,
                                       datetime.date(year, month, day)):
                    new_list.append(dataset_path)
            else:
                # Note that dataset paths that do not match the pattern
                # are included. They will be filtered on metadata by
                # AbstractIngester.
                new_list.append(dataset_path)

        return new_list

    def open_dataset(self, dataset_path):
        """Create and return a dataset object.

        dataset_path: points to the dataset to be opened and have
           its metadata read.
        """

        return LandsatDataset(dataset_path)
