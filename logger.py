import logging

def CreateMainLogger():
    logging.basicConfig(filename="yandex_bus.log",
                        format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=logging.INFO)
    logging.captureWarnings(True)
    logger = logging.getLogger('Yandex_Bus')
    logger.setLevel("INFO")
    return logger