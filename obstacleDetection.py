#!/usr/bin/env python3

import cv2
import numpy as np
from matplotlib import pyplot as plt
import imutils

from obstacle import *

class ObstacleDetection:

    def __init__(self):

        self.obstacles = []
        self.contours = None
        # self.out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))

        # HSV ranges for eliminating background
        self.hMin = 0
        self.sMin = 0
        self.vMin = 0
        self.hMax = 179
        self.sMax = 255
        self.vMax = 255

        self.lower_wall = np.array([0, 0, 30])
        self.upper_wall = np.array([80, 100, 255])

        self.lower_floor = np.array([0, 0, 40])
        self.upper_floor = np.array([150, 70, 140])

        self.lower_misc = np.array([35, 0, 50])
        self.upper_misc = np.array([185, 65, 140])

        # Image manipulation kernels
        self.kernel_erosion = np.ones((4, 4), np.uint8)
        self.kernel_dilation = np.ones((6, 6), np.uint8)
        self.kernel_open = np.ones((6, 6), np.uint8)
        self.kernel_close = np.ones((10, 10), np.uint8)

        self.count = 0

        self.frame = None
        self.img = None
        self.img_binary = None
        self.hsv_img = None
        self.img_backup = None
        self.img_gray = None
        self.edged_gray = None


    def process_frame(self):

        self.img = cv2.pyrDown(self.frame)

        self.img = cv2.copyMakeBorder(self.img, top=10, bottom=10, left=10, right=10, borderType=cv2.BORDER_CONSTANT,
                                      value=[0, 0, 0])
        self.img_backup = self.img.copy()

        # img = cv2.blur(img,(20,20))
        # img = cv2.GaussianBlur(img, (5, 5), 0)

        # Create HSV Image and threshold into a range.
        hsv_img_original = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        mask_wall = cv2.bitwise_not(cv2.inRange(hsv_img_original, self.lower_wall, self.upper_wall))
        mask_floor = cv2.bitwise_not(cv2.inRange(hsv_img_original, self.lower_floor, self.upper_floor))
        mask_misc = cv2.bitwise_not(cv2.inRange(hsv_img_original, self.lower_misc, self.upper_misc))

        # Final mask removing background stuff
        mask = cv2.bitwise_and(cv2.bitwise_and(mask_misc, mask_wall), mask_floor)

        # Image with background removed
        self.img = cv2.bitwise_and(self.img, self.img, mask=mask)
        self.hsv_img = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        # Blur colours and edges together
        self.hsv_img = cv2.erode(self.hsv_img, self.kernel_erosion, iterations=1)
        self.hsv_img = cv2.dilate(self.hsv_img, self.kernel_dilation, iterations=1)

        # self.hsv_img = cv2.morphologyEx(self.hsv_img, cv2.MORPH_OPEN, self.kernel_open)
        self.hsv_img = cv2.morphologyEx(self.hsv_img, cv2.MORPH_CLOSE, self.kernel_close)

        # hsv_img = cv2.blur(hsv_img,(4,4))
        # hsv_img = cv2.GaussianBlur(hsv_img, (5, 5), 0)

        self.img = cv2.cvtColor(self.hsv_img, cv2.COLOR_HSV2BGR)
        self.img_gray = cv2.cvtColor(self.hsv_img, cv2.COLOR_BGR2GRAY)

        thresh, self.img_binary = cv2.threshold(self.img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    def find_contours_edges(self):

        self.edged_gray = cv2.Canny(self.img_binary, 100, 200)

        self.contours, hierarchy = cv2.findContours(self.edged_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        print("num contours: " + str(len(self.contours)))


    def draw_images(self):

        total = self.get_percent_white_pixels()
        print("% of white pixels in ROI: " + str(total))

        cv2.drawContours(self.img_backup, self.contours, -1, (0, 255, 0), 3)

        if self.count == 1:
            cv2.imshow("img_binary", self.img_binary)
            cv2.moveWindow('img_binary', 0, 600)

            cv2.imshow("img_final", self.img_backup)
            cv2.moveWindow('img_final', 0, 0)
        else:
            # cv2.imshow("hsv_img", self.hsv_img)
            # cv2.imshow("edged_hsv", edged_hsv)
            cv2.imshow("img_binary", self.img_binary)
            # cv2.imshow("edged_gray", self.edged_gray)
            cv2.imshow("img_final", self.img_backup)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            exit(0)

    def detect_obstacles(self, frame, scanning, yaw):

        self.frame = frame

        self.count += 1
        obstacle_return = None

        self.process_frame()
        height, width, _ = self.img.shape

        self.find_contours_edges()

        # Match objects with contours
        for contour in self.contours:

            x, y, w, h = cv2.boundingRect(contour)
            x2 = x + w
            center = (x + x2) / 2

            # Ignore shit if its by the edges because it can be split into 2 or 3 separate shapes
            area = cv2.contourArea(contour)
            if area < 5000:
                if area > 3000: print("Object too small! " + str(area))
                continue

            left_threshold = 0.05 * width
            right_threshold = width - left_threshold

            temp = width / 2
            lower_center_threshold = temp - width * 0.2
            upper_center_threshold = temp + width * 0.2

            if x < left_threshold:
                print("Object too near left edge!")
                continue
            if x2 > right_threshold:
                print("Object too near right edge!")
                continue

            if center < lower_center_threshold or center > upper_center_threshold:
                print("Object not centered enough") # Want to make sure we have the entire shape
                continue

            if scanning:
                # Just create new obstacle, dont bother matching
                print("Creating new obstacle")
                new_obstacle = Obstacle(x, x2, frame, yaw, area)
                self.obstacles.append(new_obstacle)

                obstacle_return = new_obstacle

            else:

                match = True

                obstacle = self.match_obstacle(x, x2, yaw, width)
                if obstacle is None: match = False

                if match:
                    print("Found existing obstacle")
                    obstacle.update(x, x2, yaw, frame, area)
                    obstacle_return = obstacle
                else:
                    print("Found new obstacle somehow ...")
                    new_obstacle = Obstacle(x, x2, frame, yaw, area)
                    self.obstacles.append(new_obstacle)
                    obstacle_return = new_obstacle

            # Draw it on the frame first
            cv2.rectangle(self.img_backup, (x,y), (x+w,y+h), (0,0,255), 2)
            cv2.putText(self.img_backup, str(area), (x, y), cv2.FONT_HERSHEY_SIMPLEX , 1, (255, 0, 0) , 2, cv2.LINE_AA)

        self.draw_images()

        return obstacle_return

        # rotate until center in middle of screen (within x %), then attempt to match it, if its known but not visited
        # then visit it, if its unknown create a new object, if its known and visited ignore it and keep spinning

    def match_obstacle(self, x1, x2, yaw, width):

        a_new, b_new = calculate_range(x1, x2, yaw, width)

        for obs in self.obstacles:
            a, b = obs.get_range()

            # Check if the two obs overlap each other
            if b_new >= a and b >= a_new:
                # Match!
                # print("Matched known obstacle!")
                return obs

        # print("No match!")
        return None

    def get_percent_white_pixels(self):

        img = self.img_binary.copy()
        height, width = img.shape

        img = img[int(height / 4):int((height / 4) * 4), int(width / 5):int((width / 5) * 4)]
        count_white = cv2.countNonZero(img)
        total = img.size

        return (count_white / total) * 100
