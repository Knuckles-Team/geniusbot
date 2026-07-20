#!/usr/bin/env python3

import logging
import shutil


# This creates the log object
class Log:
    logger = None
    logging_file = ""
    logging_dir = ""

    # Initialize the Class
    def __init__(self, logging_dir=""):
        from geniusbot.services.backend_adapter import backend

        xdg_log_dir = backend.resolve_log_dir()

        xdg_log_dir.mkdir(parents=True, exist_ok=True)

        if logging_dir == "":
            self.logging_dir = str(xdg_log_dir).replace("\\", "/")
        else:
            self.logging_dir = logging_dir

        self.logging_file = str(xdg_log_dir / "geniusbot.log").replace("\\", "/")
        print("File logging initialized")
        logging.basicConfig(
            filename=self.logging_file,
            format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
            filemode="w",
            level=logging.DEBUG,
        )

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
        """Keep stdout attached to the caller instead of persisting raw output."""
        self.logger.info("Raw stdout capture is disabled by privacy policy")

    def log_stderr(self):
        """Keep stderr attached to the caller instead of persisting raw output."""
        self.logger.info("Raw stderr capture is disabled by privacy policy")

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


# Compatibility adapter for callers that explicitly provide privacy-safe text.
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        if buf and buf.strip():
            self.logger.log(
                self.log_level,
                "External stream activity: character_count=%d",
                len(buf),
            )
