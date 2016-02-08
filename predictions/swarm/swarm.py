#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
"""
Running a swarm on a file to find the best model/
"""
import os
import json
import pprint
import sys
import getopt
import logging

logging.basicConfig()

from nupic.swarming import permutations_runner

SWARM_DESCRIPTION = ""

DESCRIPTION = (
    "This script runs a swarm on the input file and\n"
    "creates a model parameters file in the `model_params` directory containing\n"
    "the best model found by the swarm."
)


def main(argv):

    if len(argv) < 2:
        printUsageAndExit(2)
    else:
        descriptionFile = argv[0]
        dataFile = argv[1]

        if os.path.isfile(descriptionFile) and os.path.isfile(dataFile):
            with open(descriptionFile) as data_file:
                global SWARM_DESCRIPTION
                SWARM_DESCRIPTION = json.load(data_file)

            swarm(dataFile)
        else:
            printUsageAndExit(3)

def printUsageAndExit(exitCode):
    print 'Usage: swarm.py path_to_description path_to_data_file'
    sys.exit(exitCode)

def modelParamsToString(modelParams):
    pp = pprint.PrettyPrinter(indent=2)
    return pp.pformat(modelParams)


def writeModelParamsToFile(modelParams, name):
    cleanName = name.replace(" ", "_").replace("-", "_")
    paramsName = "%s_model_params.py" % cleanName
    outDir = os.path.join(os.getcwd(), 'model_params')
    if not os.path.isdir(outDir):
        os.mkdir(outDir)
    outPath = os.path.join(os.getcwd(), 'model_params', paramsName)
    with open(outPath, "wb") as outFile:
        modelParamsString = modelParamsToString(modelParams)
        outFile.write("MODEL_PARAMS = \\\n%s" % modelParamsString)
    return outPath


def swarmForBestModelParams(swarmConfig, name, maxWorkers=4):
    outputLabel = name
    permWorkDir = os.path.abspath('swarm/' + name)
    if not os.path.exists(permWorkDir):
        os.mkdir(permWorkDir)
    modelParams = permutations_runner.runWithConfig(
        swarmConfig,
        {"maxWorkers": maxWorkers, "overwrite": True},
        outputLabel=outputLabel,
        outDir=permWorkDir,
        permWorkDir=permWorkDir)
    modelParamsFile = writeModelParamsToFile(modelParams, name)
    return modelParamsFile


def printSwarmSizeWarning(size):
    if size is "small":
        print "= Small swarms IS A DEBUG SWARM. DON'T EXPECT YOUR MODEL RESULTS TO BE GOOD."
    elif size is "medium":
        print "= Medium swarm. Medium swarms could take awhile."
    else:
        print "= LARGE SWARM! Large swarms take awhile!"


def swarm(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    print "================================================="
    print "= Swarming on %s data..." % name
    printSwarmSizeWarning(SWARM_DESCRIPTION["swarmSize"])
    print "================================================="
    modelParams = swarmForBestModelParams(SWARM_DESCRIPTION, name)
    print "\nWrote the following model param files:"
    print "\t%s" % modelParams


if __name__ == "__main__":
    # print DESCRIPTION
    main(sys.argv[1:])
