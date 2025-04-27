from util.command import run_command
from util.object_detection import object_detection
from util.keyframe import keyframe_extration
from util.correct import correct
import os
import cv2
import base64
import shutil
import time
import json
import shlex
import traceback


IS_TESTING = False  # 強制進入正式流程
align = False  # 或 False 看你想測哪種
error_list = [25, 10, 5]  # 假設有這些錯誤代碼
use_rate = True



def keypoint_detection():
    
    run_command("D:/my_project/mmpose", "openmmlab2", "pred_for_analyze.py")
    
    
def pose_recognition():
    
    
    model = "FCNN"
    name = "no3P"
    who = "dean"
    
    if use_rate:
        command = f"pre_rate.py --model {model} --name {name} --who {who}"
    else:
        command = f"pred.py --model {model} --name {name} --who {who}"
    
    output_std = run_command("D:/my_project/single_frame", "patchTST", command)
    
    lines = output_std.strip().splitlines()
    
    Line = [] 
    
    for line in lines:
        Line.append(line.split("_"))


    #format [[pose, number], [0,0], [1,1],.......]
    return Line



def tobase64(img_set):
    
    for i in range(len(img_set)):
        cv2.imwrite(f"{i}.jpg", img_set[i])
    
    return True

def test_pipeline(start_time):
    try:
        """
        if os.path.exists("analyze/analyze_output"):
            shutil.rmtree("analyze/analyze_output")
            
        os.makedirs("analyze/analyze_output", exist_ok=True)
        
        print("=== Step 1: Keypoint Detection ===")
        keypoint_detection()
        print(f"Step 1: {time.time()-start_time}")
        start_time = time.time()
        """
        print("=== Step 2: Keyframe Extraction ===")
        save_list = keyframe_extration()
        
        print(f"Step 2: {time.time()-start_time}")
        start_time = time.time()
        print("保留圖片：", save_list)
        
        # 刪除非關鍵幀圖片和對應 JSON
        #save_list = [67, 102, 115, 157, 235, 245, 257, 338, 348, 381, 391, 431, 442, 451, 463, 513, 522, 529, 560, 572, 578, 593, 605, 667, 673, 682, 690, 761]
        
        save_list = [int(number) for number in save_list]
        
        with open("save_list.json", "w") as f:
            json.dump(save_list, f)

        
        print("=== Step 3: Pose Recognition ===")
        pose_list = pose_recognition()
        print("姿勢辨識結果：", pose_list)
        
        print(f"Step 3: {time.time()-start_time}")
        start_time = time.time()
        
        print("=== Step 4: Correct ===")
        test_error = error_list[0]  # 假設測試第 1 種錯誤
        corrected_images = correct(pose_list, test_error, align)
        
        print(f"Step 4: {time.time()-start_time}")
        start_time = time.time()

        print("=== Step 5: toBase64 ===")
        base64_images = tobase64(corrected_images)


        print("✅ 全部流程執行完畢，沒拋出錯誤。")
        print(f"Step 1: {time.time()-start_time}")
    
    
        
    except Exception as e:
        print("❌ 測試過程中發生錯誤：", e)
        traceback.print_exc()
        
        
def sort():
    i = 0
    List = sorted(os.listdir("analyze"))
    for jpg in List:
        os.rename(f"analyze/{jpg}", f"analyze/{i}.jpg")
        i += 1

if __name__ == '__main__':
    
    
    #sort()
    
    start_time = time.time()
    test_pipeline(start_time)
