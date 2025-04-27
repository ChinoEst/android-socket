import os 
import pandas as pd
import json
import shutil
import argparse
import sys
import inspect
import random
import numpy as np
import cv2 
from scipy import interpolate






keypoints_columns = ["x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4", "x5", "y5",
             "x6", "y6", "x7", "y7", "x8", "y8", "x9", "y9", "x10", "y10",
             "x11", "y11", "x12", "y12", "x13", "y13", "x14", "y14", "x15", "y15",
             "x16", "y16", "x17", "y17", "x18", "y18", "x19", "y19", "x20", "y20",
             "x21", "y21", "x22", "y22", "x23", "y23"]

keypoint_info={
    0:
    dict(name='nose', id=0, color=[51, 153, 255], type='upper', swap=''),
    
    1:
    dict(
        name='left_eye',
        id=1,
        color=[51, 153, 255],
        type='upper',
        swap='right_eye'),
    
    2:
    dict(
        name='right_eye',
        id=2,
        color=[51, 153, 255],
        type='upper',
        swap='left_eye'),
    
    3:
    dict(
        name='left_ear',
        id=3,
        color=[51, 153, 255],
        type='upper',
        swap='right_ear'),
    
    4:
    dict(
        name='right_ear',
        id=4,
        color=[51, 153, 255],
        type='upper',
        swap='left_ear'),
    
    5:
    dict(
        name='left_shoulder',
        id=5,
        color=[0, 255, 0],
        type='upper',
        swap='right_shoulder'),
    
    6:
    dict(
        name='right_shoulder',
        id=6,
        color=[255, 128, 0],
        type='upper',
        swap='left_shoulder'),

    7:
    dict(
        name='left_elbow',
        id=7,
        color=[0, 255, 0],
        type='upper',
        swap='right_elbow'),
    
    8:
    dict(
        name='right_elbow',
        id=8,
        color=[255, 128, 0],
        type='upper',
        swap='left_elbow'),
    
    9:
    dict(
        name='left_wrist',
        id=9,
        color=[0, 255, 0],
        type='upper',
        swap='right_wrist'),
    
    10:
    dict(
        name='right_wrist',
        id=10,
        color=[255, 128, 0],
        type='upper',
        swap='left_wrist'),
    
    11:
    dict(
        name='left_hip',
        id=11,
        color=[0, 255, 0],
        type='lower',
        swap='right_hip'),
    
    12:
    dict(
        name='right_hip',
        id=12,
        color=[255, 128, 0],
        type='lower',
        swap='left_hip'),
    
    13:
    dict(
        name='left_knee',
        id=13,
        color=[0, 255, 0],
        type='lower',
        swap='right_knee'),
    
    14:
    dict(
        name='right_knee',
        id=14,
        color=[255, 128, 0],
        type='lower',
        swap='left_knee'),
    
    15:
    dict(
        name='left_ankle',
        id=15,
        color=[0, 255, 0],
        type='lower',
        swap='right_ankle'),
    
    16:
    dict(
        name='right_ankle',
        id=16,
        color=[255, 128, 0],
        type='lower',
        swap='left_ankle'),
    
    17:
    dict(name='left_finger',
         id=17,
         color=[0, 255, 0],
         type='upper',
         swap='right_finger'),
    
    18:
    dict(name='right_finger',
         id=18,
         color=[255, 128, 0],
         type='upper',
         swap='left_finger'),
    
    19:
    dict(name='left_rib',
         id=19,
         color=[0, 255, 0],
         type='upper',
         swap='right_rib'),
    
    20:
    dict(name='right_rib',
         id=20,
         color=[255, 128, 0],
         type='upper',
         swap='left_rib'),
    
    21:
    dict(name='left_toe',
         id=21,
         color=[0, 255, 0],
         type='lower',
         swap='right_toe'),
    
    22:
    dict(name='right_toe',
         id=22,
         color=[255, 128, 0],
         type='lower',
         swap='left_toe'),
}
    
skeleton_info={
    0:
    dict(link=('left_ankle', 'left_knee'), id=0, color=[0, 255, 0]),
    1:
    dict(link=('left_knee', 'left_hip'), id=1, color=[0, 255, 0]),
    2:
    dict(link=('right_ankle', 'right_knee'), id=2, color=[255, 128, 0]),
    3:
    dict(link=('right_knee', 'right_hip'), id=3, color=[255, 128, 0]),
    4:
    dict(link=('left_hip', 'right_hip'), id=4, color=[51, 153, 255]),
    5:
    dict(link=('left_shoulder', 'left_rib'), id=5, color=[51, 153, 255]),
    6:
    dict(link=('right_shoulder', 'right_rib'), id=6, color=[51, 153, 255]),
    7:
    dict(link=('left_shoulder', 'right_shoulder'), id=7, color=[51, 153, 255]),
    8:
    dict(link=('left_shoulder', 'left_elbow'), id=8, color=[0, 255, 0]),
    9:
    dict(link=('right_shoulder', 'right_elbow'), id=9, color=[255, 128, 0]),
    10:
    dict(link=('left_elbow', 'left_wrist'), id=10, color=[0, 255, 0]),
    11:
    dict(link=('right_elbow', 'right_wrist'), id=11, color=[255, 128, 0]),
    12:
    dict(link=('left_eye', 'right_eye'), id=12, color=[51, 153, 255]),
    13:
    dict(link=('nose', 'left_eye'), id=13, color=[51, 153, 255]),
    14:
    dict(link=('nose', 'right_eye'), id=14, color=[51, 153, 255]),
    15:
    dict(link=('left_eye', 'left_ear'), id=15, color=[51, 153, 255]),
    16:
    dict(link=('right_eye', 'right_ear'), id=16, color=[51, 153, 255]),
    17:
    dict(link=('left_ear', 'left_shoulder'), id=17, color=[51, 153, 255]),
    18:
    dict(link=('right_ear', 'right_shoulder'), id=18, color=[51, 153, 255]),
    19:
    dict(link=('left_rib', 'left_hip'), id=19, color=[51, 153, 255]),
    20:
    dict(link=('right_rib', 'right_hip'), id=20, color=[51, 153, 255]),
    21:
    dict(link=('left_wrist', 'left_finger'), id=21, color=[0, 255, 0]),
    22:
    dict(link=('right_wrist', 'right_finger'), id=22, color=[255, 128, 0]),
    23:
    dict(link=('left_ankle', 'left_toe'), id=23, color=[0, 255, 0]),
    24:
    dict(link=('right_ankle', 'right_toe'), id=24, color=[255, 128, 0])
    
}

    
file_name = "analyze/analyze_output/67.json"

with open(file_name, "r") as file:
    j_data = json.load(file)
    j_data = j_data[0]
       
    
img = cv2.imread("analyze/67.jpg")
keypoint = {}
for j in range(23): 
    #read keypoints coordinate in old frame -> coordinate in new canvas
    x = int(j_data["keypoints"][j][0] )
    y = int(j_data["keypoints"][j][1] )
    img = cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
    keypoint[f"{j}"] = (x,y)
    
for i in range(25):
    link = skeleton_info[i]["link"]
    k1 = link[0]
    k2 = link[1]
    
    keypoint1_id = [k for k, v in keypoint_info.items() if v['name'] == k1][0]
    keypoint2_id = [k for k, v in keypoint_info.items() if v['name'] == k2][0]
    
    point1 = keypoint[str(keypoint1_id)]
    point2 = keypoint[str(keypoint2_id)]
    
    
    color = skeleton_info[i]["color"]

    img = cv2.line(img, point1, point2, color, 2)
    cv2.imwrite(f"skeleton.jpg", img)








                    
    
