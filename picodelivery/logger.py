import logging


def setupCustomLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # create a file handler
    handler = logging.FileHandler(name + '.log')
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger
