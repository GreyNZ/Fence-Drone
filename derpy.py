#!/usr/bin/env python3

from easytello import tello

#from obstacleDetection import *
#from obstacle import *

import cv2
import numpy as np

import time
import threading


class FrontEnd(object):

    def __init__(self):
        self.iteration = 0
        self.tello = tello.Tello() # Tello object for drone interaction
        #self.detector = FenceDetection()
        self.frame = None

    def streamon(self):
        self.tello.send_command('streamon') # Send command to turn on video stream from tello drone
        video_thread = threading.Thread(target=self._video_thread)
        video_thread_daemon = True
        video_thread.start()

    def _video_thread(self):
        cap = cv2.VideoCapture('udp://' + self.tello.tello_ip + ':11111')
        while True:
            ret, self.frame = cap.read()

    def run(self):

        self.streamon()
        while self.frame is None:
            continue
        time.sleep(1)

        scanning = True

        print(f'\nBattery: {self.tello.get_battery()}\n')
        print(f'Temp: {self.tello.get_temp()}\n\n')

        self.tello.takeoff()
        self.tello.down(0.2)
        #self.tello.up(0.5)

        yaw = int(self.tello.get_attitude()[2])

        start_orientation = yaw

        time.sleep(0.2) # just to know where i am
        print('\nSleep: A\n')
        time.sleep(0.2) # just to know where i am


        should_stop = False
        counter = 0

        while not should_stop:

            print(f'\nIn loop, iter {counter}\n')

            self.tello.forward(20)
            self.tello.set_speed(50)
            self.tello.forward(25)
            time.sleep(2)
            self.tello.set_speed(10)
            self.tello.forward(100)
            time.sleep(2)

            counter += 1
            if counter > 0:
                should_stop = True

            # self.tello.cw(45)
            # self.tello.ccw(45)

            # self.tello.back(0.2)
            # self.tello.forward(0.2)
            # self.tello.right(0.3)
            # self.tello.left(0.3)

            # self.tello.down(0.2)
            # self.tello.up(0.2)


        self.tello.land()
        self.tello.send_command('streamoff')

        cv2.destroyAllWindows()
        quit(0)


def main():
    frontend = FrontEnd()
    frontend.run()  # run frontend


if __name__ == '__main__':
    main()
