"""
Used to create a model for the run program using NuPIC.
Should be able to dynamically swarm between areas.
Should be provided with just the areas id number and the rest can be selected from there..
"""
import os
import json
import pprint
import sys
import logging
from nupic.swarming import permutations_runner

logging.basicConfig()

SWARM_DESCRIPTION = ""

DESCRIPTION = (
    "This script runs a swarm on the input file and\n"
    "creates a model parameters file in the `model_params` directory containing\n"
    "the best model found by the swarm."
)


def main(argv):

    if len(argv) < 1:
        printUsageAndExit(2)
    else:
        areaId = argv[0]

        areaDirPath = "area_data/area_" + areaId + "/"
        descriptionFile = "swarm_description_placeholder.json"
        area_aggregates_filepath = areaDirPath + "area_aggregates_" + areaId + ".csv"

        if not os.path.isfile(area_aggregates_filepath):
            print "Unable to find aggregate data file at %s" % area_aggregates_filepath
            printUsageAndExit(3)

        if not os.path.isdir(areaDirPath):
            print "Unable to find area directory at %s" % areaDirPath
            printUsageAndExit(4)

        if os.path.isfile(descriptionFile):
            with open(descriptionFile) as data_file:
                global SWARM_DESCRIPTION
                SWARM_DESCRIPTION = json.load(data_file)

                print "Altering swarm_description placeholder to use area specific aggregate csv file"
                SWARM_DESCRIPTION["streamDef"]["streams"][0]["source"] = "file://" + area_aggregates_filepath

            swarm(areaId, areaDirPath)
        else:
            printUsageAndExit(3)


def printUsageAndExit(exitCode):
    print 'Usage: swarm.py area_id'
    sys.exit(exitCode)


def modelParamsToString(modelParams):
    pp = pprint.PrettyPrinter(indent=2)
    return pp.pformat(modelParams)


def writeModelParamsToFile(modelParams, outputDir):
    paramsName = "model_params.py"
    outputFilePath = os.path.join(outputDir, paramsName)

    with open(outputFilePath, "wb") as outFile:
        modelParamsString = modelParamsToString(modelParams)  # Converting the modelparams to a string
        outFile.write("MODEL_PARAMS = \\\n%s" % modelParamsString)  # Writing parameter string to the actual file

    return outputFilePath


def swarmForBestModelParams(swarmConfig, areaDirPath, maxWorkers=4):
    """
    Trigger the swarm passing the configuration file to the permutation runner in NuPIC.
    Also trigger the writing of the resultant model params file
    """
    # TODO Check this is correct naming..
    outputLabel = "model_params"

    # Define where the work will take place (Should be in the area1 folder, in a tmp_work folder?)
    # Need the path to the area1 folder to do this...
    permuWorkDir = os.path.abspath(areaDirPath + "tmpWork")
    outputDir = os.path.abspath(areaDirPath)

    createDirIfNotExisting(permuWorkDir)
    createDirIfNotExisting(outputDir)

    modelParams = permutations_runner.runWithConfig(
        swarmConfig,
        {"maxWorkers": maxWorkers, "overwrite": True},
        outputLabel=outputLabel,
        outDir=outputDir,
        permWorkDir=permuWorkDir)

    modelParamsFilePath = writeModelParamsToFile(modelParams, outputDir)

    return modelParamsFilePath


def createDirIfNotExisting(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def swarm(areaId, areaDirPath):
    print "================================================="
    print "= Running a " + SWARM_DESCRIPTION["swarmSize"] + " sized swarm for area %s" % areaId
    print "================================================="
    modelParamsFilePath = swarmForBestModelParams(SWARM_DESCRIPTION, areaDirPath)
    print "\nWrote the model param file to %s" % modelParamsFilePath


if __name__ == "__main__":
    # print DESCRIPTION
    main(sys.argv[1:])
