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

import logging
from agdc.ls7_ingester import LS7Ingester

# Start ingest process
if __name__ == "__main__":

    #pylint:disable=invalid-name
    #
    # Top level variables are OK if this is the top level script.
    #

    ingester = LS7Ingester()

    if ingester.args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    ingester.ingest(ingester.args.source_dir)

    ingester.collection.cleanup()

