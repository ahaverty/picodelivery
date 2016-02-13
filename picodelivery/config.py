import ConfigParser


def getConfig(configLocation):
    config = ConfigParser.ConfigParser()
    config.read(configLocation)
    return config
