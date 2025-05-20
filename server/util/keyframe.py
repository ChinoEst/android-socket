import os
import re
import json
from scipy.ndimage import gaussian_filter1d
import numpy as np
from scipy.signal import find_peaks
import eventlet
import logging
from eventlet import tpool


def keyframe_extraction(result_list):
    logging.info("[INFO] keyframe_extraction start!")
    keypoint_list = result_list["keypoints"]
    bbox_list = result_list["bbox"]
    
    del_list = sorted([19, 20], reverse=True)
    sigma = 2
    min_valley_length = 1
    diff_threshold = 70

    def diff(tent, pre):
        x1, y1 = tent
        x2, y2 = pre
        
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    

        
        
    try:
        for_plt_x = []
        for_plt_y = []
        buffer = 0
        pre = []
        for i in range(0, len(keypoint_list)):
                                
            if len(pre) == 0:
                pre = keypoint_list[i]
                        
            else:
                for j in range(23):
                    if not j in del_list:
                        loss = diff(keypoint_list[i][j], pre[j])
                        #full[f"{i}"].append(loss)
                        buffer += loss
                        
                for_plt_x.append(i)
                for_plt_y.append(buffer)
                
                pre = keypoint_list[i]
                
            buffer = 0
        
        for_plt_y = gaussian_filter1d(for_plt_y, sigma)
        
        y = np.array(for_plt_y)
        
        
        
        valleys, _ = find_peaks(-y)         
        keyframes = []
        
        
        for i in range(1, len(valleys)):
            valley_index = valleys[i]
            if y[valley_index] < diff_threshold:
                keyframes.append(valley_index)

        keypoint_result = [keypoint_list[int(x)] for x in keyframes]
        
        bbox_result = [bbox_list[int(x)] for x in keyframes]
        #print(bbox_result)
        idx = [int(x) for x in keyframes]
        
        result = {"keypoints":keypoint_result, "bbox":bbox_result, "idx": idx}
        
                

        logging.info(f"idx:{idx}")
        logging.info("[INFO] keyframe_extraction finish!")
        return result
    except Exception as e:
        logging.error(f"[ERROR] keyframe_extraction error: {str(e)}", exc_info=True)
        print(str(e))

  