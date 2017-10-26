import os
import threading
import logging
import time
import cv2 # pylint: disable=import-error
from picamera.array import PiRGBArray # pylint: disable=import-error
from picamera import PiCamera # pylint: disable=import-error

class Detector(object):
    """Detects faces and place those images in queue"""

    def __init__(self, queue, imshow=False):
        if not queue:
            raise ValueError("'queue' is required")
        self._logger = logging.getLogger(__name__)
        self._queue = queue
        self._imshow = imshow
        self._stop_event = threading.Event()
        self._thread = None
        self._face_cascade = None
        self._cascade_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),\
            "haarcascade_frontalface_default.xml")

    def start(self):
        self._thread = threading.Thread(target=self._process_stream)
        self._thread.daemon = True
        self._thread.start()

    def _process_stream(self):
        self._logger.info("Starting detector...")

        self._face_cascade = cv2.CascadeClassifier(self._cascade_file_path)
        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        camera.resolution = (1280, 720)
        camera.framerate = 32
        raw_capture = PiRGBArray(camera, size=(1280, 720))
        time.sleep(0.1)

        for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
            self._process_frame(frame.array)
            raw_capture.truncate(0)
            if self._stop_event.is_set():
                break

        cv2.destroyAllWindows()

    def _process_frame(self, frame):
        # check blurriness before processing image detection
        bluerness = cv2.Laplacian(frame, cv2.CV_64F).var()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if  bluerness < 50:
            self._logger.debug("Detected bluered face with score %s.", bluerness)
        else:
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)

            if len(faces) > 0:
                self._logger.debug("Detected %d faces with bluerness %d.", len(faces), bluerness)

                self._queue.put(cv2.imencode('.jpg', frame)[1].tobytes())

                if self._imshow:
                    for (coord_x, coord_y, width, height) in faces:
                        cv2.rectangle(gray,\
                            (coord_x, coord_y),\
                            (coord_x+width, coord_y+height),\
                            (0, 255, 0), 2)

        # display image if non-headless
        if self._imshow:
            cv2.imshow("Faces", gray)
            cv2.waitKey(1)

    def stop(self):
        self._logger.info("Stopping detector...")
        self._stop_event.set()
        self._thread.join()
        self._logger.info("Detector finished")
