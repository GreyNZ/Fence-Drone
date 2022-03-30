#!/usr/bin/env python3

import cv2
import numpy as np
from matplotlib import pyplot as plt
import imutils

class FaceDetection:

    def __init__(self):
        self.frame = None
        self.img = None
        self.img_copy = None
        self.faces = None

    def process_frame(self):
        self.img = cv2.pyrDown(self.frame)
        self.img_copy = self.img.copy()
        detect_face()

    def draw_images(self):
        print('draw screens')
        cv2.imshow("img_video_feed", self.img)
        cv2.imshow("faces_feed", self.faces)

    def detect_face():
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        face_rectange = face_cascade.detectMultiScale(self.img_copy)
        for (x,y,w,h) in face_rectange:
            cv2.rectangle(img,(x,y),(x+w,y+h),(30,255,30),2)
        draw_images()





