"""
Used to create a model for the run program using NuPIC.
Should be able to dynamically swarm between areas.
Should be provided with just the areas id number and the rest can be selected from there..
"""
import json
import os
import pprint
import sys

from nupic.swarming import permutations_runner

from picodelivery import logger

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
	
	realDir = os.path.dirname(os.path.realpath(__file__)) + "/"
	
        areaDirPath = realDir + "area_data/area_" + str(areaId) + "/"
        descriptionFile = realDir + "swarm_description_placeholder.json"
        area_aggregates_filepath = areaDirPath + "area_" + str(areaId) + "_aggregates.csv"

        if not os.path.isfile(area_aggregates_filepath):
            log.error("Unable to find aggregate data file at %s" % area_aggregates_filepath)
            printUsageAndExit(3)

        if not os.path.isdir(areaDirPath):
            log.error("Unable to find area directory at %s" % areaDirPath)
            printUsageAndExit(4)

        if os.path.isfile(descriptionFile):
            with open(descriptionFile) as data_file:
                global SWARM_DESCRIPTION
                SWARM_DESCRIPTION = json.load(data_file)

                log.info("Altering swarm_description placeholder to use area specific aggregate csv file")
                SWARM_DESCRIPTION["streamDef"]["streams"][0]["source"] = "file://" + area_aggregates_filepath

            swarm(areaId, areaDirPath)
        else:
            printUsageAndExit(3)


def printUsageAndExit(exitCode):
    print 'Usage: swarm.py area_id'
    log.error("Exiting program with exit code %s" % exitCode)
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
    log.info("Running a %s sized swarm for area %s" % (SWARM_DESCRIPTION["swarmSize"], areaId))

    modelParamsFilePath = swarmForBestModelParams(SWARM_DESCRIPTION, areaDirPath)
    log.info("Wrote the model param file to %s" % modelParamsFilePath)


if __name__ == "__main__":
    log = logger.setupCustomLogger(sys.argv[0])
    main(sys.argv[1:])
