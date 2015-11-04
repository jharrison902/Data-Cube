#!/usr/bin/env python

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


__author__ = "Simon Oldfield"


import logging
from datacube.api import parse_date_min, parse_date_max, Satellite, DatasetType
from datacube.api.query import list_cells_as_list, list_tiles_as_list
from datacube.api.query import list_cells_vector_file_as_list
from datacube.api.query import MONTHS_BY_SEASON, Season
from datacube.api.query import LS7_SLC_OFF_EXCLUSION, LS7_SLC_OFF_ACQ_MIN
from datacube.api.query import LS8_PRE_WRS_2_EXCLUSION, LS8_PRE_WRS_2_ACQ_MAX


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


_log = logging.getLogger()


TEST_CELL_X = 120
TEST_CELL_Y = -25
TEST_YEAR = 2005
TEST_YEAR_STR = str(TEST_YEAR)
TEST_MONTHS = MONTHS_BY_SEASON[Season.SUMMER]

TEST_VECTOR_FILE = "Mainlands.shp"
TEST_VECTOR_LAYER = 0
TEST_VECTOR_FEATURE = 4


def test_list_cells_120_020_2005_ls578(config=None):

    cells = list_cells_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR), acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=[DatasetType.ARG25],
                               config=config)

    assert(cells and len(list(cells)) > 0)

    for cell in cells:
        _log.info("Found cell xy = %s", cell.xy)
        assert(cell.x == TEST_CELL_X and cell.y == TEST_CELL_Y and cell.xy == (TEST_CELL_X, TEST_CELL_Y))


def test_list_cells_120_020_2005_ls578_no_ls7_slc(config=None):

    cells = list_cells_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR),
                               acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=[DatasetType.ARG25],
                               exclude=[LS7_SLC_OFF_EXCLUSION],
                               config=config)

    assert(cells and len(list(cells)) > 0)

    for cell in cells:
        _log.info("Found cell xy = %s", cell.xy)
        assert(cell.x == TEST_CELL_X and cell.y == TEST_CELL_Y and cell.xy == (TEST_CELL_X, TEST_CELL_Y))


def test_list_cells_120_020_2005_ls578_no_ls8_pre_wrs_2(config=None):

    cells = list_cells_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR), acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=[DatasetType.ARG25],
                               exclude=[LS8_PRE_WRS_2_EXCLUSION],
                               config=config)

    assert(cells and len(list(cells)) > 0)

    for cell in cells:
        _log.info("Found cell xy = %s", cell.xy)
        assert(cell.x == TEST_CELL_X and cell.y == TEST_CELL_Y and cell.xy == (TEST_CELL_X, TEST_CELL_Y))


def test_list_cells_120_020_2005_ls578_summer(config=None):

    cells = list_cells_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR), acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=[DatasetType.ARG25],
                               months=TEST_MONTHS,
                               config=config)

    assert(cells and len(list(cells)) > 0)

    for cell in cells:
        _log.info("Found cell xy = %s", cell.xy)
        assert(cell.x == TEST_CELL_X and cell.y == TEST_CELL_Y and cell.xy == (TEST_CELL_X, TEST_CELL_Y))


def test_list_tiles_120_020_2005_ls578(config=None):

    dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]

    tiles = list_tiles_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR), acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=dataset_types,
                               config=config)

    assert(tiles and len(list(tiles)) > 0)

    for tile in tiles:
        _log.info("Found tile xy = %s", tile.xy)
        assert(tile.x == TEST_CELL_X and tile.y == TEST_CELL_Y and tile.xy == (TEST_CELL_X, TEST_CELL_Y)
               and tile.end_datetime_year == TEST_YEAR
               and ds in tile.datasets for ds in dataset_types)


def test_list_tiles_120_020_2005_ls578_no_ls7_slc(config=None):

    dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]

    tiles = list_tiles_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR),
                               acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=dataset_types,
                               exclude=[LS7_SLC_OFF_EXCLUSION],
                               config=config)

    assert(tiles and len(list(tiles)) > 0)

    for tile in tiles:
        _log.info("Found tile xy = %s", tile.xy)

        dataset = tile.datasets[DatasetType.ARG25]
        assert dataset
        _log.info("Found ARG25 dataset [%s]", dataset.path)

        assert(tile.x == TEST_CELL_X and tile.y == TEST_CELL_Y and tile.xy == (TEST_CELL_X, TEST_CELL_Y)
               and tile.end_datetime_year == TEST_YEAR
               and (ds in tile.datasets for ds in dataset_types)
               and (dataset.satellite != Satellite.LS7 or tile.end_datetime.date() <= LS7_SLC_OFF_ACQ_MIN))


def test_list_tiles_120_020_2005_ls578_no_ls8_pre_wrs_2(config=None):

    dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]

    tiles = list_tiles_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR),
                               acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=dataset_types,
                               exclude=[LS8_PRE_WRS_2_EXCLUSION],
                               config=config)

    assert(tiles and len(list(tiles)) > 0)

    for tile in tiles:
        _log.info("Found tile xy = %s", tile.xy)

        dataset = tile.datasets[DatasetType.ARG25]
        assert dataset
        _log.info("Found ARG25 dataset [%s]", dataset.path)

        assert(tile.x == TEST_CELL_X and tile.y == TEST_CELL_Y and tile.xy == (TEST_CELL_X, TEST_CELL_Y)
               and tile.end_datetime_year == TEST_YEAR
               and (ds in tile.datasets for ds in dataset_types)
               and (dataset.satellite != Satellite.LS8 or tile.end_datetime.date() >= LS8_PRE_WRS_2_ACQ_MAX))


def test_list_tiles_120_020_2005_ls578_summer(config=None):

    dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]

    tiles = list_tiles_as_list(x=[TEST_CELL_X], y=[TEST_CELL_Y],
                               acq_min=parse_date_min(TEST_YEAR_STR),
                               acq_max=parse_date_max(TEST_YEAR_STR),
                               satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                               dataset_types=dataset_types,
                               months=TEST_MONTHS,
                               config=config)

    assert(tiles and len(list(tiles)) > 0)

    for tile in tiles:
        _log.info("Found tile xy = %s", tile.xy)
        assert(tile.x == TEST_CELL_X and tile.y == TEST_CELL_Y and tile.xy == (TEST_CELL_X, TEST_CELL_Y)
               and tile.end_datetime_year == TEST_YEAR
               and (ds in tile.datasets for ds in dataset_types)
               and tile.end_datetime_month in [m.value for m in TEST_MONTHS])


# AOI

def test_list_cells_act_2005_ls578(config=None):
    cells = list_cells_vector_file_as_list(vector_file=TEST_VECTOR_FILE,
                                           vector_layer=TEST_VECTOR_LAYER,
                                           vector_feature=TEST_VECTOR_FEATURE,
                                           satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
                                           acq_min=parse_date_min(TEST_YEAR_STR),
                                           acq_max=parse_date_max(TEST_YEAR_STR),
                                           dataset_types=[DatasetType.ARG25], config=None)

    assert(cells and len(list(cells)) == 2)

    for cell in cells:
        _log.info("Found cell xy = %s", cell.xy)
        assert((cell.x == 148 or cell.x == 149) and cell.y == -36)


# def test_list_tiles_act_2005_ls578(config=None):
#
#     dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]
#
#     tiles = list_tiles_vector_file_as_list(vector_file="Mainlands.shp", vector_layer=0, vector_feature=4,
#                                            acq_min=parse_date_min("2005"), acq_max=parse_date_max("2005"),
#                                            satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
#                                            dataset_types=dataset_types,
#                                            config=config)
#
#     assert(tiles and len(list(tiles)) > 0)
#
#     for tile in tiles:
#         _log.info("Found tile xy = %s", tile.xy)
#         assert((tile.x == 148 or tile.x == 149) and tile.y == -36
#                and tile.end_datetime_year == 2005
#                and (ds in tile.datasets for ds in dataset_types)
#                and tile.end_datetime_month in [m.value for m in MONTHS_BY_SEASON[Season.SUMMER]])


# def test_list_tiles_act_2005_ls578_summer(config=None):
#
#     dataset_types = [DatasetType.ARG25, DatasetType.PQ25, DatasetType.FC25]
#
#     tiles = list_tiles_vector_file_as_list(vector_file="Mainlands.shp", vector_layer=0, vector_feature=4,
#                                            acq_min=parse_date_min("2005"), acq_max=parse_date_max("2005"),
#                                            satellites=[Satellite.LS5, Satellite.LS7, Satellite.LS8],
#                                            dataset_types=dataset_types,
#                                            months=MONTHS_BY_SEASON[Season.SUMMER],
#                                            config=config)
#
#     assert(tiles and len(list(tiles)) > 0)
#
#     for tile in tiles:
#         _log.info("Found tile xy = %s", tile.xy)
#         assert((tile.x == 148 or tile.x == 149) and tile.y == -36
#                and tile.end_datetime_year == 2005
#                and (ds in tile.datasets for ds in dataset_types)
#                and tile.end_datetime_month in [m.value for m in MONTHS_BY_SEASON[Season.SUMMER]])

