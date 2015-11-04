# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:08:42 2015

ama.jdh

AMA LS8 Ingester

"""

import os
import logging
import argparse

from abc import ABCMeta, abstractmethod
import psycopg2,sys

from agdc import DataCube
from agdc.abstract_ingester import Collection
from agdc.abstract_ingester import AbstractDataset
from agdc.abstract_ingester import AbstractBandstack
from agdc.abstract_ingester import AbstractIngester
from agdc.ls8_ingester.ls8dataset import LS8Dataset
from agdc.cube_util import DatasetError, DatasetSkipError, parse_date_from_string

logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.INFO)

#
# Set up logger (for this module).
#

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class LS8Ingester(AbstractIngester):
    """Ingester class for Landsat datasets."""

    @classmethod
    def arg_parser(cls):
        """Make a parser for required args."""

        # Extend the default parser
        _arg_parser = super(LS8Ingester, cls).arg_parser()

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
        

        dataset_list = [os.path.abspath(scenedir)
                        for scenedir in source_dir.split(',')
                        if scenedir]

        if self.args.fast_filter:
            dataset_list = self.fast_filter_datasets(dataset_list)

        return dataset_list

    def fast_filter_datasets(self, dataset_list):
        """Filter a list of dataset paths by path/row and date range."""

        return dataset_list

    def open_dataset(self, dataset_path):
        """Create and return a dataset object.

        dataset_path: points to the dataset to be opened and have
           its metadata read.
        """

        return LS8Dataset(dataset_path)
