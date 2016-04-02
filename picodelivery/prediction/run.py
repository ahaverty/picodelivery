"""
Class for running data through the NuPIC predictor and and saving model state to file.
@author alanhaverty@student.dit.ie
"""

import imp
import os

from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

from picodelivery import logger

log = logger.setupCustomLogger(__name__)


class Run(object):
    def __init__(self, modelParamsPath, savedModelsPath, steps):
        """
        Initialise the class with setup variables and metric manager
        :param modelParamsPath: The model params pather to use if no saved models path is found
        :param savedModelsPath: The models path where the model is persisted to file
        :param steps: The number of steps to predict into the future
        :return:
        """
        self.modelParamsPath = modelParamsPath
        self.savedModelsPath = savedModelsPath
        self.fieldToPredict = "numberOfDeliveries"
        self.steps = steps

        self.metricSpecs = self.defineMetricSpecs()
        self.model = self.getModel()

        self.metricsManager = MetricsManager(self.metricSpecs, self.model.getFieldInfo(), self.model.getInferenceType())

    def createModelFromParams(self, modelParams):
        """
        Creates a model fromt the provided model parameters file
        :param modelParams:
        :return:
        """
        model = ModelFactory.create(modelParams)
        model.enableInference({"predictedField": self.fieldToPredict})
        return model

    def defineMetricSpecs(self):
        """
        Define the metric properties for nupic model
        :return:
        """
        metricSpecs = (
            MetricSpec(field=self.fieldToPredict, metric='multiStep',
                       inferenceElement='multiStepBestPredictions',
                       params={'errorMetric': 'aae', 'window': 1000, 'steps': self.steps}),
            MetricSpec(field=self.fieldToPredict, metric='trivial',
                       inferenceElement='prediction',
                       params={'errorMetric': 'aae', 'window': 1000, 'steps': self.steps}),
            MetricSpec(field=self.fieldToPredict, metric='multiStep',
                       inferenceElement='multiStepBestPredictions',
                       params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': self.steps}),
            MetricSpec(field=self.fieldToPredict, metric='trivial',
                       inferenceElement='prediction',
                       params={'errorMetric': 'altMAPE', 'window': 1000, 'steps': self.steps})
        )
        return metricSpecs

    def getModelParams(self):
        """
        Get the model parameters object
        :return:
        """
        log.info("Importing model params from %s" % self.modelParamsPath)
        moduleName = os.path.basename(self.modelParamsPath)
        importedModelParams = imp.load_source(moduleName, self.modelParamsPath)
        return importedModelParams.MODEL_PARAMS

    def getModel(self):
        """
        Get the existing model from file or create
        from model params if not already existing
        :return:
        """
        # Check if the dir is empty
        if os.path.exists(self.savedModelsPath) and os.listdir(self.savedModelsPath):
            log.info("Loading model from checkpoint %s" % self.savedModelsPath)
            model = ModelFactory.loadFromCheckpoint(self.savedModelsPath)
        else:
            log.info("Creating model from %s..." % self.modelParamsPath)
            model = self.createModelFromParams(self.getModelParams())

        return model

    def predict(self, timestamp, amountOfJobs):
        """
        Run a single timestamp and amount value through nupic
        and return the prediction for the next hour of jobs
        :param timestamp:
        :param amountOfJobs:
        :return:
        """
        result = self.model.run({
            "timestamp": timestamp,
            self.fieldToPredict: float(amountOfJobs)
        })
        result.metrics = self.metricsManager.update(result)

        prediction = float(result.inferences["multiStepBestPredictions"][self.steps])

        return prediction

    def saveModel(self):
        """
        Save the model to file
        :return:
        """
        log.info("Saving model to %s..." % self.savedModelsPath)
        self.model.save(self.savedModelsPath)
