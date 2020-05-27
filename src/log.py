import logging
import os
import sys


# This creates the log object for all of GeniusBot
class Log:
    logger = None
    logging_file = ""
    logging_dir = ""

    # Initialize the Class
    def __init__(self):
        #print("Test")
        self.logging_file = f"{os.pardir}/logs/log.log"
        self.logging_dir = f"{os.pardir}/logs/"
        #print("attempt one: ", self.logging_dir)
        if os.path.isdir(self.logging_dir):
            print("Log File: ", self.logging_file)
        else:
            self.logging_file = f"{os.curdir}/logs/log.log"
            #print("Log File: ", self.logging_file)
        logging.basicConfig(filename=self.logging_file, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                            filemode='w', level=logging.DEBUG)
        # Creating an object
        self.logger = logging.getLogger()
        # Setting the threshold of logger to DEBUG
        self.logger.setLevel(logging.DEBUG)
        # Test messages
        self.logger.debug("Debug: Initialized")
        self.logger.info("Info: Initialized")
        self.logger.warning("Warning: Initialized")
        self.logger.error("Error: Initialized")
        self.logger.critical("Critical: Initialized")
        self.logger.info("Logging Module: Initializing")
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl

        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
        self.logger.debug(sys.stdout)
        self.logger.warning(sys.stderr)
        print("Logging Initialized Successfully")

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


# This class will write to the logfile in stream format
class StreamToLogger(object):

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())