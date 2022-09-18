#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import logging


# This creates the log object
class Log:
    logger = None
    logging_file = ""
    logging_dir = ""

    # Initialize the Class
    def __init__(self, logging_dir=""):
        # Set logging directory to users' home directory
        if logging_dir == "":
            self.logging_dir = f"{os.path.expanduser('~')}".replace("\\", "/")
        else:
            self.logging_dir = logging_dir
        self.logging_file = f'{os.path.join(os.curdir, "geniusbot.log")}'.replace("\\", "/")
        if os.path.isdir(self.logging_dir):
            print("Log File: ", self.logging_file)
        else:
            self.logging_file = f'{os.path.join(os.curdir, "geniusbot.log")}'.replace("\\", "/")
            print("Log File: ", self.logging_file)
        logging.basicConfig(filename=self.logging_file, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                            filemode='w', level=logging.DEBUG)

    # Kick Off Log Initializing
    def init_logging(self):
        # Creating an object
        self.logger = logging.getLogger()
        # Setting the threshold of logger to INFO
        self.logger.setLevel(logging.INFO)
        # Test messages
        # self.logger.debug("Debug: Initialized")
        self.logger.info("Info: Initialized")
        self.logger.warning("Warning: Initialized")
        self.logger.error("Error: Initialized")
        self.logger.critical("Critical: Initialized")
        self.logger.info("Logging Module: Initializing")

    def log_stdout(self):
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        self.logger.debug(sys.stdout)

    def log_stderr(self):
        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
        self.logger.warning(sys.stderr)

    # Write msg to Log as Debug Line
    def debug(self, msg):
        self.logger.debug(msg)

    # Write msg to Log as Info Line
    def info(self, msg):
        self.logger.info(msg)

    # Write msg to Log as Warning Line
    def warning(self, msg):
        self.logger.warning(msg)

    # Write msg to Log as Error Line
    def error(self, msg):
        self.logger.error(msg)

    # Write msg to Log as Critical Line
    def critical(self, msg):
        self.logger.critical(msg)

    # Set logwriter file location
    def set_logfile(self, filepath):
        self.logging_file = filepath

    # Get logwriter file location
    def get_logfile(self):
        return self.logging_file

    # Log Dump
    def get_log_dump(self):
        shutil.copy(self.logging_file, f"{self.logging_dir}log_dump.txt")


# This class will write to the logfile in stream format
class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
