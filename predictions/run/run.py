import os
import imp
import logger

from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

log = logger.setupCustomLogger(__name__)

class Run(object):

    def __init__(self, modelParamsPath, savedModelsPath, steps):
        self.modelParamsPath = modelParamsPath
        self.savedModelsPath = savedModelsPath
        self.fieldToPredict = "numberOfDeliveries"
        self.steps = steps

        self.metricSpecs = self.defineMetricSpecs()
        self.model = self.getModel()

        self.metricsManager = MetricsManager(self.metricSpecs, self.model.getFieldInfo(), self.model.getInferenceType())

    def createModelFromParams(self, modelParams):
        model = ModelFactory.create(modelParams)
        model.enableInference({"predictedField": self.fieldToPredict})
        return model

    def defineMetricSpecs(self):
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
        log.info("Importing model params from %s" % self.modelParamsPath)
        moduleName = os.path.basename(self.modelParamsPath)
        importedModelParams = imp.load_source(moduleName, self.modelParamsPath)
        return importedModelParams.MODEL_PARAMS

    def getModel(self):
        #Check if the dir is empty
        if os.path.exists(self.savedModelsPath) and os.listdir(self.savedModelsPath) :
            log.info( "Loading model from checkpoint %s" % self.savedModelsPath)
            model = ModelFactory.loadFromCheckpoint(self.savedModelsPath)
        else:
            log.info( "Creating model from %s..." % self.modelParamsPath)
            model = self.createModelFromParams(self.getModelParams())

        return model

    def predict(self, timestamp, amountOfJobs):

        result = self.model.run({
            "timestamp": timestamp,
            self.fieldToPredict: float(amountOfJobs)
        })
        result.metrics = self.metricsManager.update(result)

        prediction = float(result.inferences["multiStepBestPredictions"][self.steps])

        return prediction

    def saveModel(self):
        log.info( "Saving model to %s..." % self.savedModelsPath)
        self.model.save(self.savedModelsPath)
