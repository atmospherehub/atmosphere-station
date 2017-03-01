from __future__ import print_function
import os
import threading
import time
import cv2 # pylint: disable=import-error
from imutils.video import VideoStream

from settings import CROP_AREA_X, CROP_AREA_Y, BLURRINESS_THRESHOLD


class Detector(object):
    """Detects faces and place those images in queue"""

    def __init__(self, queue, imshow=False):
        if not queue:
            raise ValueError("'queue' is required")
        self._queue = queue
        self._imshow = imshow
        self._stop_event = threading.Event()
        self._thread = None
        self._cascade_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),\
            "haarcascade_frontalface_default.xml")

    def start(self):
        self._thread = threading.Thread(target=self._process_stream)
        self._thread.daemon = True
        self._thread.start()

    def _process_stream(self):
        print("Starting detector...")

        face_cascade = cv2.CascadeClassifier(self._cascade_file_path)
        stream = VideoStream(src=0).start()
        time.sleep(2.0)
        while not self._stop_event.is_set():
            frame = stream.read()

            cropped_frame = frame[CROP_AREA_Y[0]:CROP_AREA_Y[1], CROP_AREA_X[0]:CROP_AREA_X[1]]

            # Checking blurriness
            if cv2.Laplacian(cropped_frame, cv2.CV_64F).var() < BLURRINESS_THRESHOLD:
                continue

            gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
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
                    for (coord_x, coord_y, width, height) in faces:
                        cv2.rectangle(frame,\
                            (coord_x, coord_y),\
                            (coord_x+width, coord_y+height),\
                            (0, 255, 0), 2)

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
