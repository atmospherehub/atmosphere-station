import threading
import Queue
import logging
import requests
from metrology import Metrology

class Sender(object):
    """Sends images that finds in queue"""

    def __init__(self, endpoint, queue, workers=1):
        if not endpoint:
            raise ValueError("'endpoint' is required")
        if not queue:
            raise ValueError("'queue' is required")
        self._logger = logging.getLogger(__name__)
        self._endpoint = endpoint
        self._queue = queue
        self._workers = workers
        self._stop_event = threading.Event()
        self._threads = []
        self._counter_failed = Metrology.counter('Files failed')

    def start(self):
        for i in range(1, self._workers + 1):
            thread = threading.Thread(target=self._process_queue, args=(i,))
            thread.daemon = True
            thread.start()
            self._threads.append(thread)

    def _process_queue(self, thread_number):
        self._logger.info("Starting sender '%d'...", thread_number)
        while not self._stop_event.is_set():
            try:
                image = self._queue.get(True, 1)
            except Queue.Empty:
                continue

            try:
                self._send_file(image, thread_number)
            except Exception:
                self._logger.exception("Error sending file in thread %d", thread_number)
                self._counter_failed.increment()

            self._logger.debug("Waiting in queue to be sent %d", self._queue.qsize())

        self._logger.info("Sender '%d' finished", thread_number)

    @Metrology.timer('File sending')
    def _send_file(self, file_to_send, thread_number):
        result = requests.post(self._endpoint,\
            files={"file": file_to_send}, timeout=20)
        self._logger.debug("De-queued by %d and sent with status %s:%s",\
            thread_number, result.status_code, result.text)
        result.close()

    def stop(self):
        self._logger.info("Stopping senders...")
        self._stop_event.set()
        for thread in self._threads:
            thread.join()
