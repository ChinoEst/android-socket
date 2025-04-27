import os
import re
import json
from scipy.ndimage import gaussian_filter1d
import numpy as np
from scipy.signal import find_peaks



def read_jason(path):
    temp = []
    with open(path, 'r') as file:
        json_data = json.load(file)
        j_data = json_data[0]
        
    for j in range(23):
        
        x = int(j_data["keypoints"][j][0])
        y = int(j_data["keypoints"][j][1])

        temp.append((x,y))


    return temp   



def diff(tent, pre):
    x1, y1 = tent
    x2, y2 = pre
    
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5



def keyframe_extration():
    
    path = 'analyze/analyze_output'
    
    List = [jason for jason in os.listdir(path) if jason.endswith(".json")]
    sorted_file_list = sorted(List, key=lambda x: tuple(map(int, re.findall(r'\d+', x))))
    #print(sorted_file_list)
    
    del_list = sorted([19, 20], reverse=True)
    frame = 5
    sigma = 2
    pre = []
    buffer = 0
    for_plt_x = []
    for_plt_y = []
    
    #full = {str(i): [] for i in range(23) if not i in del_list}
    

    for i in range(0, len(List), frame):
        if os.path.exists(f"{path}/{i}.json"):            
            
            temp = read_jason(f"{path}/{i}.json")
            
            if len(pre) == 0:
                pre = temp
                        
            else:
                for i in range(23):
                    if not i in del_list:
                        loss = diff(temp[i], pre[i])
                        #full[f"{i}"].append(loss)
                        buffer += loss
                        
                for_plt_x.append(i)
                for_plt_y.append(buffer)
                
                pre = temp
            
            buffer = 0
    
    for_plt_y = gaussian_filter1d(for_plt_y, sigma)
    
    
    y = np.array(for_plt_y)
    
    
    valleys, _ = find_peaks(-y)
    min_valley_length = 1
    diff_threshold = 25
    
    keyframes = []
    
    
    for i in range(1, len(valleys)):
        valley_index = valleys[i]
        if y[valley_index] < diff_threshold:
            keyframes.append(valley_index * frame)

            
    
    #return list of name of image
    return keyframes