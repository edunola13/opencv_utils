import sys
import socket
import cv2
import threading
import logging
import numpy

from enola_opencv_utils.rw_frames import VideoCapture


class SocketConnectionThread(threading.Thread):
    def __init__(self, clientsocket, com_url, opened_cameras):
        threading.Thread.__init__(self)

        self.url = com_url
        self.sockets = []
        self.sockets.append(clientsocket)
        self.opened_cameras = opened_cameras
        path = self.url
        try:
            # For local cameras
            path = int(self.url)
        except:
            pass
        self.video = VideoCapture(path)

    def run(self):
        while 1:
            try:
                ret, frame = self.video.read()
                if not ret:
                    self.die()
                data = cv2.imencode('.jpg', frame)[1].tostring()
                if len(self.sockets):
                    for c in self.sockets:
                        self.send(c, data)
                else:
                    self.video.release()
                    self.die()
            except KeyboardInterrupt:
                self.signal_handler()

    def send(self, c, data):
        try:
            c.send(data)
            c.send(b"END!")  # send param to end loop in client
        except socket.error:
            logging.info("Remove client for camera")
            self.sockets.remove(c)

    def die(self):
        logging.info("Socket Camera Connection Die")
        try:
            for c in self.sockets:
                c.close()
        except:
            pass
        del self.opened_cameras[self.url]
        exit(0)

    def add_connection(self, client):
        self.sockets.append(client)


class SocketServerCamerasThread(threading.Thread):

    def __init__(self, host="", port=5005):
        threading.Thread.__init__(self)
        self.opened_cameras = {}
        self.host = host
        self.port = port

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        logging.info("Server started")
        logging.info("Waiting for client request..")
        while True:
            try:
                clientsock, clientAddress = server.accept()
                # Reveice the camera path
                cam_url = clientsock.recv(1024)
                # if camera url does not exsists in opened camera, open new connection,
                # or else just append client params and pass to Connection thread
                cam_url = cam_url.decode("utf-8")
                if cam_url not in self.opened_cameras:
                    logging.info("New Camera")
                    client = SocketConnectionThread(clientsock, cam_url, self.opened_cameras)
                    self.opened_cameras[cam_url] = client
                    client.start()
                else:
                    logging.info("New Client for Camera")
                    self.opened_cameras[cam_url].add_connection(clientsock)
            except Exception as e:
                logging.error(e)


class SocketClientCameraThread(threading.Thread):

    def __init__(self, host="localhost", port=5005, name='', cam_url='0'):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.name = name
        self.cam_url = cam_url

    def run(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.connect((self.host, self.port))
        client.send(str.encode(self.cam_url))

        while True:
            try:
                data = b''
                while True:
                    try:
                        r = client.recv(90456)
                        if len(r) == 0:
                            exit(0)
                        a = r.find(b'END!')
                        if a != -1:
                            data += r[:a]
                            break
                        data += r
                    except Exception as e:
                        print(e)
                        continue
                nparr = numpy.fromstring(data, numpy.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if type(frame) is type(None):
                    pass
                else:
                    self.process_frame(client, frame)
            except Exception as e:
                logging.error(e)

    def process_frame(self, client, frame):
        try:
            cv2.imshow(self.name, frame)
            if cv2.waitKey(10) == ord('q'):
                client.close()
                sys.exit()
        except:
            client.close()
            exit(0)
