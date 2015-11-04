# ===============================================================================
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
# ===============================================================================

"""
Ingest WOfS tiles into the Data Cube.

Example usage:

Ingest all datasets within a folder (searched recursively):

    python -m agdc.wofs_ingester -C datacube.conf --source /path/to/datasets

Or a specific dataset:

    python -m agdc.wofs_ingester -C datacube.conf --source LS7_ETM_WATER_140_-027_2013-08-18T00-26-16.880864.tif

"""
from __future__ import absolute_import

import logging
from .abstract_ingester.pretiled import GdalMdDataset, PreTiledIngester
from . import abstract_ingester


_LOG = logging.getLogger(__name__)


def _is_water_file(f):
    """
    Is this the filename of a water file?
    :type f: str
    :rtype: bool

    >>> _is_water_file('LS7_ETM_WATER_144_-037_2007-11-09T23-59-30.500467.tif')
    True
    >>> _is_water_file('createWaterExtents_r3450_3752.log')
    False
    >>> _is_water_file('LC81130742014337LGN00_B1.tif')
    False
    >>> _is_water_file('LS8_OLITIRS_OTH_P51_GALPGS01-032_113_074_20141203')
    False
    >>> # We only currently care about the Tiffs:
    >>> _is_water_file('LS_WATER_150_-022_1987-05-27T23-23-00.443_2014-03-10T23-55-40.796.nc')
    False
    """
    return 'WATER' in f and f.endswith('.tif')


class WofsIngester(PreTiledIngester):
    """Ingester class for WOfS tiles."""
    def __init__(self, datacube=None, collection=None):
        super(WofsIngester, self).__init__(_is_water_file, datacube, collection)

    def open_dataset(self, dataset_path):
        """Create and return a dataset object.
        :type: dataset_path: str
        """
        return WofsDataset(dataset_path)


class WofsDataset(GdalMdDataset):
    """
    Water extent tile.

    All metadata is read from our default gdal properties.

    We may want to read some of the custom WOfS properties here in the future (?)
    """
    pass


if __name__ == '__main__':
    abstract_ingester.run_ingest(WofsIngester)
