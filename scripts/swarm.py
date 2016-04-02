"""
Used to create a model for the run program using NuPIC.
When triggered, the swarm will look for the csv file containing
the aggregated data.
This should have a few thousand rows of data, but no more than 3000
(As recommended by NuPIC)
@author alanhaverty@student.dit.ie
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
    descriptionFile = realDir + "../configuration/swarm_description_placeholder.json"

    areaDirPath = realDir + "../area_data/area_" + str(areaId) + "/"
    area_aggregates_filepath = areaDirPath + "area_" + str(areaId) + "_aggregates.csv"

    area_stream_def_info_name = "area_" + str(areaId) + "_stream_def"
    area_stream_info_name = "area_" + str(areaId) + "_stream"
    area_stream__source = "file://" + area_aggregates_filepath

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

            log.info("Altering swarm_description placeholder to use area specific data.")
            log.info("== Using streamDef.info: " + area_stream_def_info_name)
            log.info("== Using streamDef.streams.0.info: " + area_stream_info_name)
            log.info("== Using streamDef.streams.0.source: " + area_stream__source)

            SWARM_DESCRIPTION["streamDef"]["info"] = area_stream_def_info_name
            SWARM_DESCRIPTION["streamDef"]["streams"][0]["info"] = area_stream_info_name
            SWARM_DESCRIPTION["streamDef"]["streams"][0]["source"] = area_stream__source

        swarm(areaId, areaDirPath)
    else:
        printUsageAndExit(5)


def printUsageAndExit(exitCode):
    print 'Usage: swarm.py area_id'
    log.error("Exiting program with exit code %s" % exitCode)
    sys.exit(exitCode)


def modelParamsToString(modelParams):
    pp = pprint.PrettyPrinter(indent=2)
    return pp.pformat(modelParams)


def writeModelParamsToFile(modelParams, outputDir):
    """
    Save the model parameters data to a file
    (This is later used by the nupic 'run' predictor to create a model from)
    :param modelParams:
    :param outputDir:
    :return:
    """
    paramsName = "model_params.py"
    outputFilePath = os.path.join(outputDir, paramsName)

    with open(outputFilePath, "wb") as outFile:
        modelParamsString = modelParamsToString(modelParams)  # Converting the modelparams to a string
        outFile.write("MODEL_PARAMS = \\\n%s" % modelParamsString)  # Writing parameter string to the actual file

    return outputFilePath


def swarmForBestModelParams(swarmConfig, areaDirPath, areaId, maxWorkers=4):
    """
    Trigger the swarm passing the configuration file to the permutation runner in NuPIC.
    Also trigger the writing of the resultant model params file
    :param swarmConfig:
    :param areaDirPath:
    :param areaId:
    :param maxWorkers:
    :return:
    """
    outputLabel = "model_params"

    # Define where the work will take place (Should be in the area1 folder, in a tmp_work folder?)
    # Need the path to the area1 folder to do this...
    permuWorkDir = os.path.abspath(areaDirPath + "tmpWork")
    outputDir = os.path.abspath(areaDirPath)

    createDirIfNotExisting(permuWorkDir)
    createDirIfNotExisting(outputDir)

    log.info("Starting permutations_runner for area %s" % areaId)

    modelParams = permutations_runner.runWithConfig(
        swarmConfig,
        {"maxWorkers": maxWorkers, "overwrite": True},
        outputLabel=outputLabel,
        outDir=outputDir,
        permWorkDir=permuWorkDir)

    log.info("Writing swarm results to model params file for area %s" % areaId)

    modelParamsFilePath = writeModelParamsToFile(modelParams, outputDir)

    return modelParamsFilePath


def createDirIfNotExisting(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def swarm(areaId, areaDirPath):
    """
    Main trigger that calls the swarming functionality on the areaid and its directory path
    :param areaId:
    :param areaDirPath:
    :return:
    """
    log.info("Running a %s sized swarm for area %s" % (SWARM_DESCRIPTION["swarmSize"], areaId))

    modelParamsFilePath = swarmForBestModelParams(SWARM_DESCRIPTION, areaDirPath, areaId)
    log.info("Wrote the model param file to %s" % modelParamsFilePath)


if __name__ == "__main__":
    log = logger.setupCustomLogger(os.path.basename(__file__))
    main(sys.argv[1:])
