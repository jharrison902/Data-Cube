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

#===============================================================================
# Execute a command ignoring errors
#
# @Author: Steven Ring
#===============================================================================

from __future__ import absolute_import
import os, argparse, time


def executeWithoutFail(cmd, sleepTimeSeconds):
    ''' Execute the supplied command until it succeeds, sleeping after each failure
    '''
    while True:
        print "Launching process: %s" % cmd
        rc = os.system(cmd)
        if rc == 0:
            break
        print "Failed to launch (exitCode=%d), waiting %d seconds" % (rc, sleepTimeSeconds)
        time.sleep(sleepTimeSeconds)


if __name__ == '__main__':

    description=""
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-c', dest="command", help="command", required=True)
    parser.add_argument('-s', dest="sleepTimeSeconds", help="time to wait between execution attempts", default=60)

    args = parser.parse_args()

    executeWithoutFail(args.command, int(args.sleepTimeSeconds))
