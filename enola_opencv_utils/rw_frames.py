import time
import cv2

from threading import Thread

#
# Properties of VideoWriter and VidepCapture
# https://docs.opencv.org/3.3.1/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d
#


class VideoCapture:

    def __init__(self, path=0):
        self.path = path
        self.cap = cv2.VideoCapture(self.path)
        if not self.cap.isOpened():
            self.cap.open(self.path)

    def read(self):
        return self.cap.read()

    def is_opened(self):
        return self.cap.isOpened()

    def get(self, key):
        return self.cap.get(key)

    def set(self, key, value):
        return self.cap.set(key, value)

    #
    # Utils
    def resolution(self):
        return '{}x{}'.format(self.cap.get(3), self.cap.get(4))

    def __del__(self):
        if self.cap:
            self.cap.release()


class VideoWriter:
    def __init__(self, path, frames_per_second=20, resolution=(640, 480)):
        # Define the codec and create VideoWriter object
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('{}{}'.format(path, 'output.avi'), self.fourcc, frames_per_second, resolution)

    def save_frame(self, frame):
        self.out.write(frame)

    def __del__(self):
        self.out.release()


class ImageWriter:
    index = 1

    def __init__(self, path, extension='png'):
        self.path = path
        self.extension = 'png'

    def save_frame(self, frame):
        cv2.imwrite('{}{}_{}.{}'.format(self.path, time.strftime("%Y%m%d-%H%M%S"), self.index, self.extension), frame)
        self.index += 1


class VideoCaptureThread(VideoCapture):
    #
    # Prodria tener diferentes versiones de este que o grabe video, guarde imagenes, etc.
    # Despues los otros hilos leen de lo que va guardando
    #

    def __init__(self, path, max_queue=50, name="WebcamVideoStream"):
        super().__init__(path)
        (self.grabbed, self.frame) = self.cap.read()

        # initialize the thread name
        self.name = name
        self.max_queue = max_queue

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self, queue):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=([queue]))
        # t.daemon = True
        t.start()
        return self

    def update(self, queue):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.cap.read()
            if self.grabbed:
                queue.put({'time': time.time(), 'frame': self.frame})
                self.new_frame()
                if queue.qsize() > self.max_queue:
                    # Remove
                    queue.get()
            else:
                self.fail_frame()

    def new_frame(self):
        # Do something with the new frame
        pass

    def fail_frame(self):
        # Do something when dont get new frame, for example: stop
        pass

    def read(self):
        # return the frame most recently read
        return self.grabbed, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
