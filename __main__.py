#!/usr/bin/env python
import sys
import signal
import os
import time
import Queue
import argparse
from lib.sender import Sender
from lib.detector import Detector
from lib.std_logger import StdLogger

def main():
    # get configuration of gateway from passed arguments
    parser = argparse.ArgumentParser(description="Atmosphere station")
    parser.add_argument("-e", "--endpoint", required=True, help="Endpoint address")
    parser.add_argument("-d", "--daemon", default=False,\
        help="Whether it is daemon service (e.g. headless)")
    args = parser.parse_args()

    # forward stdout to log file when running headless
    if args.daemon:
        StdLogger.register()

    # start sub-services
    _queue = Queue.Queue()
    _sender = Sender(args.endpoint, _queue, 1)
    _detector = Detector(_queue, not args.daemon)

    signal.signal(signal.SIGTERM, lambda signal, frame: _term_handler(_sender, _detector))

    _sender.start()
    _detector.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    _term_handler(_sender, _detector)
    return 0

def _term_handler(sender, detector):
    detector.stop()
    sender.stop()
    sys.exit(0)

sys.exit(main())
