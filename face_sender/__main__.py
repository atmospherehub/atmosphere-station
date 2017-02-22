import sys
import signal
import os
import time
import Queue
from sender import Sender
from detector import Detector

def main():
    _queue = Queue.Queue()
    _sender = Sender(os.environ["ATMOSPHERE_ENDPOINT"], _queue, 1)
    _detector = Detector(_queue, False)

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
