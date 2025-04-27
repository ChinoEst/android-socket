from util.command import run_command
import json


def object_detection(w, h):
    

    working_dir = "D:/my_project/mmpose"
    # 使用 shell 運行命令
    run_command("{working_dir}", "openmmlab2", "pred_for_obj.py")
    
    
    #read output json
    with open(f'{working_dir}/obj_output/first.json', 'r') as file:
        json_data = json.load(file)
        j_data = json_data[0]
        

    bbox = j_data["bbox"][0]
    
    bbox_up_x = bbox[0]
    bbox_up_y = bbox[1]
    bbox_down_x = bbox[2]
    bbox_down_y = bbox[3]
    
    In = True
    
    #判斷是否接近外框
    if bbox_up_x < 20 or bbox_up_y < 20:
        In = False
    
    if w == 1080:
        if bbox_down_x > 1060 or bbox_down_y > 1900:
            In = False
    else:
        if bbox_down_y > 1060 or bbox_down_x > 1900:
            In = False
        
    return In