#!/usr/bin/env python3

from easytello import tello

from obstacleDetection import *
from obstacle import *

import cv2
import numpy as np


import time
import threading


class FrontEnd(object):

    def __init__(self):

        self.iteration = 0

        # Init Tello object that interacts with the Tello drone ------------------------------------------------------
        self.tello = tello.Tello()

        # Init the obstacle detector
        self.detector = ObstacleDetection()

        self.in_view_obstacle = None

        self.frame = None

    def streamon(self):
        self.tello.send_command('streamon')
        video_thread = threading.Thread(target=self._video_thread)
        video_thread.daemon = True
        video_thread.start()

    def _video_thread(self):

        # Creating stream capture object
        cap = cv2.VideoCapture('udp://' + self.tello.tello_ip + ':11111')

        while True:
            ret, self.frame = cap.read()

    def key_control(self):
        # screen = curses.initscr()
        # curses.noecho()
        # curses.cbreak()
        # curses.keypad(True)
        wait_time = 2
        try:
            while True:
                char = cv2.waitKey(wait_time)
                if char == ord('q'):
                    break
                elif char == 63235:
                    self.tello.right(10)
                elif char == 63234:
                    self.tello.left(10)
                elif char == 63232:
                    self.tello.up(10)
                elif char == 63233:
                    self.tello.down(10)
                elif char == ord('w'):
                    self.tello.forward(10)
                elif char == ord('s'):
                    self.tello.back(10)
                elif char == ord('a'):
                    self.tello.ccw(45)
                elif char == ord('d'):
                    self.tello.cw(45)
        finally:
            # curses.nocbreak();screen.keypad(0);curses.echo()
            # curses.endwin()
            self.tello.land()


    def run(self):

        self.streamon()
        while self.frame is None:
            continue
        time.sleep(1)

        scanning = True

        print("Battery")
        print(self.tello.get_battery())
        print("Temp")
        print(self.tello.get_temp())

        # takeoff
        self.tello.takeoff()
        self.tello.down(0.2)

        yaw = int(self.tello.get_attitude()[2])

        start_orientation = yaw

        thresh1 = start_orientation - 15
        thresh2 = start_orientation + 15

        if thresh1 < - 180: thresh1 = abs(thresh1) - 30
        if thresh2 > 180: thresh2 = - (thresh2 - 30)

        print("start: " + str(start_orientation))
        print("thresh1: " + str(thresh1))
        print("thresh2: " + str(thresh2))


        should_stop = False
        # while not should_stop:
        #     time.sleep(0.2)
        #     self.tello.flip(direc='f')
        #     time.sleep(0.2)
        #     self.tello.ccw(45)
        #     time.sleep(0.2)
        #     self.tello.forward(200)
        #     should_stop = True

        self.key_control()

        # land
        self.tello.land()
        self.tello.send_command('streamoff')

        cv2.destroyAllWindows()

        quit(0)


def main():
    frontend = FrontEnd()

    # run frontend
    frontend.run()


if __name__ == '__main__':
    main()
