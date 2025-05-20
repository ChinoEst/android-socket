import eventlet
eventlet.monkey_patch()

import json
import requests  
import logging
from multiprocessing import Process, Queue


def detection_worker(w, h, input_path, queue):
    MMPOSE_API_URL = "http://localhost:8000/predict_obj"
    #print(input_path)
    try:
        #call mmpose
        response = requests.post(
            f"{MMPOSE_API_URL}/",
            json={"file_path": input_path}
        )
        result = response.json()
        
        #in cemera or not
        j_data = result["predictions"][0][0]
        bbox = j_data["bbox"][0]
        bbox_up_x, bbox_up_y = bbox[0], bbox[1]
        bbox_down_x, bbox_down_y = bbox[2], bbox[3]
        
        #in cemera or not
        In = True
        if bbox_up_x < 20 or bbox_up_y < 20:
            In = False
        if w == 1080:
            if bbox_down_x > 1060 or bbox_down_y > 1900:
                In = False
        else:
            if bbox_down_y > 1060 or bbox_down_x > 1900:
                In = False
        logging.error("Object Detection success")
        
        queue.put({"success": True, "in_image": In})
        
    except Exception as e:
        logging.error(f"Object Detection Error: {e}")
        queue.put({"success": False, "error": str(e)})



def object_detection(w, h, input_path, callback):
    queue = Queue()
    p = Process(target=detection_worker, args=(w, h, input_path, queue))
    p.start()
    def wait_result():
        #wait for queue return
        result = queue.get()
        callback(result)
    eventlet.spawn(wait_result)

    
    