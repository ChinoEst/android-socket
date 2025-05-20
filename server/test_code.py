import eventlet
eventlet.monkey_patch()

from util.keypoint_detection import keypoint_detection_batch
from util.keyframe import keyframe_extraction
from util.pose_recognition import async_predict as pose_recognition
from util.correct import correct
import json


def on_keypoint_done(results):
    eventlet.spawn(keyframe_extraction, results, on_keyframes_done)
    

def on_keyframes_done(keyframes):
    try:
        print("on_keyframes_done 被呼叫，型別：", type(keyframes))
        if isinstance(keyframes, str):
            print("上一層出錯：", keyframes)
            return
        eventlet.spawn(pose_recognition, keyframes, on_pose_done)
        print("pose recognition finished")
    except Exception as e:
        print("on_keyframes_done 發生例外：", e)

def on_pose_done(poses):
    try:
        print("on_pose_done 被呼叫，型別：", type(poses))
        if isinstance(poses, str):
            print("上一層出錯：", poses)
            return
        image_set = correct(poses, error, align, status)
        print("image finish")
    except Exception as e:
        print("on_pose_done 發生例外：", e)














if __name__ == '__main__':
    
    
    global status, error, align
    
    status = "test"
    
    error = 15
    
    align = False
    
    input_path = f"D:/my_project/android-camera-socket-stream-master/server/{status}/analyze"
    
    keypoint_detection_batch(input_path, on_keypoint_done)
    
    """
    with open("temp.json", "r", encoding="utf-8") as f:
        results = json.load(f)
        
    print("temp.json 結構：", type(results), results.keys())
    
    print("keypoint detection finished")
    keyframe_extraction(results, on_keyframes_done)
    """
    
    eventlet.sleep(10)
    input("123")
    