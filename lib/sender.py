from __future__ import print_function
import threading
import Queue
import requests

class Sender(object):
    """Sends images that finds in queue"""

    def __init__(self, endpoint, queue, workers=1):
        if not endpoint:
            raise ValueError("'endpoint' is required")
        if not queue:
            raise ValueError("'queue' is required")
        self._endpoint = endpoint
        self._queue = queue
        self._workers = workers
        self._stop_event = threading.Event()
        self._threads = []

    def start(self):
        for i in range(1, self._workers + 1):
            thread = threading.Thread(target=self._process_queue, args=(i,))
            thread.daemon = True
            thread.start()
            self._threads.append(thread)

    def _process_queue(self, thread_number):
        print("Starting sender '%d'..." % thread_number)
        while not self._stop_event.is_set():
            try:
                image = self._queue.get(True, 1)
            except Queue.Empty:
                continue

            try:
                result = requests.post(self._endpoint,\
                    files={"file": image}, timeout=10)
                print("De-queued by %d and sent with status %s:%s , waiting in queue %d"\
                    % (thread_number, result.status_code, result.text, self._queue.qsize()))
                result.close()
            except Exception as ex:
                print("Error in '%d' sending %s" % (thread_number, ex))

        print("Sender '%d' finished" % thread_number)

    def stop(self):
        print("Stopping senders...")
        self._stop_event.set()
        for thread in self._threads:
            thread.join()
