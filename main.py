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

        # Init Tello object that interacts with the Tello drone --------------------
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

        # First run we find all obstacles
        while scanning:

            # Spin and scan
            self.tello.cw(20)

            yaw = int(self.tello.get_attitude()[2])
            print("cur: " + str(yaw))

            new_obstacle = self.detector.detect_obstacles(self.frame, scanning, yaw)

            time.sleep(0.2)

            if thresh1 < yaw < thresh2 or thresh2 < yaw < thresh1:
                scanning = False

                dif = start_orientation - yaw
                print("Done scanning, correction required of: " + str(dif))
                if dif > 2:
                    self.tello.cw(dif)
                elif dif > -2:
                    self.tello.ccw(abs(dif))

        print(len(self.detector.obstacles))
        for obs in self.detector.obstacles:
            print(obs)


        should_stop = False
        while not should_stop:

            self.tello.cw(20)

            #self.tello.flip('left')

            yaw = int(self.tello.get_attitude()[2])
            print("cur yaw: " + str(yaw))

            in_view_obstacle = self.detector.detect_obstacles(self.frame, scanning, yaw)

            if in_view_obstacle is not None:
                if not in_view_obstacle.visited:
                    # visit it!

                    print("% of white pixels in ROI: " + str(self.detector.get_percent_white_pixels()))
                    self.tello.forward(0.2)
                    print("% of white pixels in ROI: " + str(self.detector.get_percent_white_pixels()))

                    self.tello.back(0.2)

                    print("Trying to visit/find obstacle")

                    for obs in self.detector.obstacles:
                        if in_view_obstacle.id == obs.id:
                            obs.visited = True
                            print("Visited obstacle!")

                else:
                    # update its stats?
                    print("Already visited this obstacle!")

            all_visited = True
            for obs in self.detector.obstacles:
                if obs.visited is False:
                    all_visited = False

            if all_visited:
                break
                print("Done!")

            else:
                print("Keep looking!")

        time.sleep(30)
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
