from .cosolvents import *

import logging

import multiprocessing_logging
multiprocessing_logging.install_mp_handler()

logging_level = logging.INFO

def get_module_logger(name, logfile):
    
    logger = logging.getLogger()

    formatter = logging.Formatter(
          '%(asctime)s - %(levelname)-8s - '
          '%(name)-22s - %(process)d - %(message)s',
          '%Y-%m-%d %H:%M:%S')

    stream_handler = logging.StreamHandler()

    stream_handler.setFormatter(formatter)
    
    file_handler = logging.FileHandler(logfile,  mode='w')
    
    file_handler.setFormatter(formatter)
    
    logger.addHandler(stream_handler)
    
    logger.addHandler(file_handler)
    
    logger.setLevel(logging_level)
    
    return logger

def set_logging_level(level):
    global logging_level
    logging_level = level