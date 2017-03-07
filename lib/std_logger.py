import logging
import logging.handlers

class StdLogger(object):
    """Class to capture stdout and sterr in the log"""

    @staticmethod
    def register_file():
        """Forward logs to file"""

        atm_logger = logging.getLogger()
        atm_logger.setLevel(logging.INFO)

        # Make a handler that writes to a file, making a new file at midnight and
        # keeping 3 backups
        handler = logging.handlers.TimedRotatingFileHandler(
            "/tmp/atmosphere-station.log", when="midnight", backupCount=3)

        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-4s %(message)s'))
        atm_logger.addHandler(handler)

    @staticmethod
    def register_console():
        """Forward logs to console"""

        atm_logger = logging.getLogger()
        atm_logger.setLevel(logging.DEBUG)

        # Make a handler that writes to a file, making a new file at midnight and
        # keeping 3 backups
        handler = logging.StreamHandler()

        handler.setFormatter(logging.Formatter("%(asctime)s:%(msecs)d %(levelname)-4s %(message)s",\
            "%H:%M:%S"))
        atm_logger.addHandler(handler)
