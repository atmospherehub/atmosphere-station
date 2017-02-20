from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import datetime
import imutils
import time
import cv2
import threading
import sys
import signal
import Queue
import requests

def start_detector(queue, stop_event):
    def _process_stream(queue, stop_event):
        print("Starting detector...")
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        stream = VideoStream(src=0).start()
        time.sleep(2.0)

        while not stop_event.is_set():
            frame = stream.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)

            if len(faces) > 0:
                queue.put(cv2.imencode('.jpg', frame)[1].tobytes())
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                print("Detected %d faces." % len(faces))

            cv2.imshow("Faces", frame)
            cv2.waitKey(1)

        cv2.destroyAllWindows()
        stream.stop()
        print("Detector finished")

    thread = threading.Thread(target=_process_stream, args=(queue, stop_event))
    thread.daemon = True
    thread.start()
    return thread

def start_sender(queue, stop_event):
    def _process_queue(queue, stop_event):
        print("Starting sender...")
        while not stop_event.is_set():
            try:
                image = queue.get(True, 1)
            except Queue.Empty:
                continue

            try:
                result = requests.post("http://posttestserver.com/post.php?dir=faces",\
                    files={"file": image}, timeout=10)
                print("De-queued and sent with status %s:%s , waiting in queue %d"\
                    % (result.status_code, result.text, queue.qsize()))
                result.close()
            except Exception as ex:
                print("Error sending %s, waiting in queue %d" % (ex, queue.qsize()))

        print("Sender finished")

    thread = threading.Thread(target=_process_queue, args=(queue, stop_event))
    thread.daemon = True
    thread.start()
    return thread

def main():
    _stop_event = threading.Event()
    _threads = []
    _queue = Queue.Queue()

    signal.signal(signal.SIGTERM, lambda signal, frame: _term_handler(_stop_event, _threads))

    _threads.append(start_detector(_queue, _stop_event))
    _threads.append(start_sender(_queue, _stop_event))
    _threads.append(start_sender(_queue, _stop_event))
    _threads.append(start_sender(_queue, _stop_event))

    # start consumer and block main thread
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    _term_handler(_stop_event, _threads)
    return 0

def _term_handler(stop_event, threads):
    """Handles SIGTERM"""
    stop_event.set()
    for thread in threads:
        thread.join()
    sys.exit(0)

sys.exit(main())