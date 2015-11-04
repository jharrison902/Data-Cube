# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 15:08:42 2015

ama.jdh

AMA LS7 Ingester

"""

import os
import sys
import datetime
import re
import logging
import argparse
import xml.etree.ElementTree as ET
from EOtools.execute import execute
from agdc.abstract_ingester import AbstractIngester
from landsat_dataset import LandsatDataset

#
# Set up root logger
#
# Note that the logging level of the root logger will be reset to DEBUG
# if the --debug flag is set (by AbstractIngester.__init__). To recieve
# DEBUG level messages from a module do two things:
#    1) set the logging level for the module you are interested in to DEBUG,
#    2) use the --debug flag when running the script.
#

logging.basicConfig(filename='/tilestore/logs/ingest.log',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    level=logging.INFO)

#
# Set up logger (for this module).
#

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class LS7Ingester(AbstractIngester):
    """Ingester class for Landsat datasets."""

    @staticmethod
    def parse_args():
        """Parse the command line arguments for the ingester.

        Returns an argparse namespace object.
        """
        LOGGER.debug('  Calling parse_args()')

        _arg_parser = argparse.ArgumentParser()

        _arg_parser.add_argument('-C', '--config', dest='config_file',
            # N.B: The following line assumes that this module is under the agdc directory
            default=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'agdc_default.conf'),
            help='LandsatIngester configuration file')

        _arg_parser.add_argument('-d', '--debug', dest='debug',
            default=False, action='store_const', const=True,
            help='Debug mode flag')

        _arg_parser.add_argument('--source', dest='source_dir',
            required=True,
            help='Source root directory containing datasets')

        follow_symlinks_help = \
            'Follow symbolic links when finding datasets to ingest'
        _arg_parser.add_argument('--followsymlinks',
                                 dest='follow_symbolic_links',
                                 default=False, action='store_const',
                                 const=True, help=follow_symlinks_help)

        fast_filter_help = 'Filter datasets using filename patterns.'
        _arg_parser.add_argument('--fastfilter', dest='fast_filter',
                                 default=False, action='store_const',
                                 const=True, help=fast_filter_help)

        sync_time_help = 'Synchronize parallel ingestions at the given time'\
            ' in seconds after 01/01/1970'
        _arg_parser.add_argument('--synctime', dest='sync_time',
                                 default=None, help=sync_time_help)

        sync_type_help = 'Type of transaction to syncronize with synctime,'\
            + ' one of "cataloging", "tiling", or "mosaicking".'
        _arg_parser.add_argument('--synctype', dest='sync_type',
                                 default=None, help=sync_type_help)

        return _arg_parser.parse_args()

    def find_datasets(self, source_dir):
        """Return a list of path to the datasets under 'source_dir'.
        Datasets should be standard ls7 SR products with modified xml

        """

        LOGGER.info('Searching for datasets in %s', source_dir)
        if self.args.follow_symbolic_links:
            command = "find -L %s -name '*.xml' | sort" % source_dir
        else:
            command = "find %s -name '*.xml' | sort" % source_dir
        LOGGER.debug('executing "%s"', command)
        result = execute(command)
        assert not result['returncode'], \
            '"%s" failed: %s' % (command, result['stderr'])

        dataset_list = [os.path.abspath(sourcedir, scenedir)
                        for scenedir in result['stdout'].split('\n')
                        if scenedir]

        #if self.args.fast_filter:
            # no filters
            #dataset_list = self.fast_filter_datasets(dataset_list)

        return dataset_list

    def fast_filter_datasets(self, dataset_list):
        return dataset_list

    def open_dataset(self, dataset_path):
        """Create and return a dataset object.

        dataset_path: points to the dataset to be opened and have
           its metadata read.
        """

        return LS7Dataset(dataset_path)

