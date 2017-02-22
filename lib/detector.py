from __future__ import print_function
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import threading
import Queue

class Detector(object):
    """Detects faces and place those images in queue"""

    def __init__(self, queue, imshow=False):
        if not queue:
            raise ValueError("'queue' is required")
        self._queue = queue
        self._imshow = imshow
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._process_stream)
        self._thread.daemon = True
        self._thread.start()

    def _process_stream(self):
        print("Starting detector...")

        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        stream = VideoStream(src=0).start()
        time.sleep(2.0)
        while not self._stop_event.is_set():
            frame = stream.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)

            if len(faces) > 0:
                print("Detected %d faces." % len(faces))
                
                self._queue.put(cv2.imencode('.jpg', frame)[1].tobytes())
                
                if self._imshow:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if self._imshow:
                cv2.imshow("Faces", frame)
                cv2.waitKey(1)

        cv2.destroyAllWindows()
        stream.stop()
        print("Detector finished")

    def stop(self):
        print("Stopping detector...")
        self._stop_event.set()
        self._thread.join()
