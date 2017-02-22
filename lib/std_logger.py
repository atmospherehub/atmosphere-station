import sys
import logging
import logging.handlers

LOG_FILENAME = "/tmp/atmosphere-station.log"

class StdLogger(object):
    """Class to capture stdout and sterr in the log"""

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        """Only log if there is a message (not just a new line)"""

        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

    @staticmethod
    def register():
        """Replace stdout with logging to file at INFO and ERROR level"""

        atm_logger = logging.getLogger("atmosphere-station")
        atm_logger.setLevel(logging.INFO)

        # Make a handler that writes to a file, making a new file at midnight and
        # keeping 3 backups
        handler = logging.handlers.TimedRotatingFileHandler(
            LOG_FILENAME, when="midnight", backupCount=3)

        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
        atm_logger.addHandler(handler)

        sys.stdout = StdLogger(atm_logger, logging.INFO)
        sys.stderr = StdLogger(atm_logger, logging.ERROR)
