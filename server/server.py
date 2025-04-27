from flask import Flask 
from flask_socketio import SocketIO
from engineio.payload import Payload
import base64
import json
import cv2
import os
import shutil
import logging
import numpy as np
from util.command import run_command
from util.object_detection import object_detection
from util.keyframe import keyframe_extration
from util.correct import correct
from queue import Queue
import threading
import gc
import psutil
import time
from flask import request


client_sid = None



#flask應用配置
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
Payload.max_decode_packets = 500
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', engineio_logger=True)


#java測試
IS_TESTING = True


# 全局變量
#mmpose
model = "FCNN"
name = "no3P"
who = "dean"
error_list = [20, 10, 5]
align = False
use_rate = True
image_counter = 0
image_queue = Queue()
transfer_timeout = 2  # 幾秒內沒再收到就算傳送完畢
transfer_timer = None  # 用來儲存 threading.Timer 物件
client_timers = {}


# 初始化日誌記錄
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')






def save_image_worker():
    global image_counter
    while True:
        img = image_queue.get()
        try:
            os.makedirs("analyze", exist_ok=True)
            img_path = f"analyze/{image_counter}.jpg"
            cv2.imwrite(img_path, img)
            image_counter += 1
            print(f"[INFO] Saved {img_path}")
            #print("Memory used (MB):", psutil.virtual_memory().used / 1024 / 1024)
            #print("CPU percent:", psutil.cpu_percent())
        except Exception as e:
            print(f"[ERROR] While saving image: {e}")
        finally:
            del img
            gc.collect()

def on_transfer_timeout():
    global client_sid
    print("== on_transfer_timeout triggered ==")
    try:
        socketio.emit('response2', {'success': True, 'message': 'All images received'}, broadcast=True)
    except Exception as e:
        print(f"[ERROR] Failed to emit response2: {e}")





def keypoint_detection():
    
    run_command("D:/my_project/mmpose", "openmmlab2", "pred_for_analyze.py")
        



def pose_recognition(save_list):
    
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


def for_test(image_folder):
    
    images_to_send = []
    
    if not os.path.exists(image_folder):
        return images_to_send
    
    for i in range(0,min(100,len(os.listdir(image_folder))),10):
        image_path = os.path.join(image_folder, f"{i}.jpg")
        with open(image_path, "rb") as img_file:
            base64_string = base64.b64encode(img_file.read()).decode("utf-8")
            
            images_to_send.append({"data": base64_string})

    return images_to_send




def tobase64(img_set):
    images_to_send= []
    for img in img_set:
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode("utf-8")
    
        images_to_send.append({"data": img_base64})  
    
    return images_to_send


"""
@socketio.on('connect')
def handle_connect():
    print(f"[INFO] Client {request.sid} connected")

    # 建立一個每10秒發送訊息的背景執行緒
    def emit_periodically(sid):
        while True:
            socketio.emit('response4', {'success': True}, to=sid)
            print(f"[INFO] Sent response4 to {sid}")
            socketio.sleep(1)  

    # 啟動新 thread
    timer_thread = socketio.start_background_task(emit_periodically, request.sid)
    client_timers[request.sid] = timer_thread
    
@socketio.on('disconnect')
def handle_disconnect():
    print(f"[ERROR] Client {request.sid} disconnected")

    # 可選：可以想辦法清理 client_timers 裡的資料
    if request.sid in client_timers:
        del client_timers[request.sid]
"""



@socketio.on('transfer')
def handleImage(data):
    global image_counter 
    global transfer_timer
    global client_sid
    client_sid = request.sid
    
    try:

        if "message" in data and "first" in data:
            
            base64_img = data["message"]
            first = data["first"]
            
            
            
            img_data = base64.b64decode(base64_img)  # 解碼 base64 影像數據
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # 轉換為 OpenCV 影像格式
            
            
            if first:
                
                
                #判斷是否在鏡頭內
                os.makedirs("tmp_obj", exist_ok=True)
                if os.path.exists("analyze"):
                    shutil.rmtree("analyze")
                os.mkdir("analyze")
                
                cv2.imwrite("tmp_obj/first.jpg", img)
                h, w, c = img.shape
                
                if not IS_TESTING:
                    #input: D:/my_project/android-camera-socket-stream-master/server/tmp
                    #output(json): D:/my_project/android-camera-socket-stream-master/server/tmp/obj_output
                    success = object_detection(w, h) #output:bool
                
                else:
                    success = True


                #回傳obj detection
                socketio.emit('response1', {'success': success})  # 返回布尔值
                print("response1 finish")
                image_counter = 0
            else:
                
                #已正式開始拍攝

                image_queue.put(img)
                
                # 重置 timeout timer
                if transfer_timer:
                    transfer_timer.cancel()
                transfer_timer = threading.Timer(transfer_timeout, on_transfer_timeout)
                transfer_timer.start()
                
            

            
            
    except Exception as e:
        print(f"Onresponse1 Error: {e}")




#拍攝圖片處理
@socketio.on('analyze')
def analyze(msg):
    print('analyze get')
    try:
        error = error_list[int(msg)-1]
        if not IS_TESTING:
            
            if os.path.exists("analyze/analyze_output"):
                shutil.rmtree("analyze/analyze_output")
                
            os.makedirs("analyze/analyze_output", exist_ok=True)
            
            #keypoint detection
            #input(jpg): D:/my_project/android-camera-socket-stream-master/server/analyze
            #output(json): D:/my_project/android-camera-socket-stream-master/server/analyze/analyze_output
            keypoint_detection()
            
            
            
            #關鍵幀擷取 大量圖片->少量圖片
            save_list = keyframe_extration()
            
            
            save_list = [int(x) for x in save_list]
            
            with open("save_list.json", "w") as f:
                json.dump(save_list, f)
            
            
            #input: D:/my_project/android-camera-socket-stream-master/server/analyze/analyze_output
            List = pose_recognition()
            
            
            
            
            image_set = correct(List, error, align)
            
            images_to_send = tobase64(image_set) 
            
        else:
            success = True
            path = "D:/my_project/android-camera-socket-stream-master/server/analyze"
            images_to_send = for_test(path)
        
            
            
            success = True
            time.sleep(5)
            socketio.emit('response3', {'success': success, 'images': images_to_send})  
            print("response3 finish")
    
    except Exception as e:
        print(f"Onresponse3 Error: {e}")


if __name__ == '__main__':
    threading.Thread(target=save_image_worker, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000)
    