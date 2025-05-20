import eventlet
eventlet.monkey_patch()

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
from util.object_detection import object_detection
from util.keypoint_detection import keypoint_detection_batch
from util.keyframe import keyframe_extraction
from util.correct import correct
from util.pose_recognition import pose_recognition
import gc
import time
from flask import request
from eventlet.queue import LightQueue
from eventlet import tpool
from concurrent.futures import ThreadPoolExecutor




client_sid = None



#flask set
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
Payload.max_decode_packets = 500
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    transports=['websocket'],  
    logger=True,
    engineio_logger=False #heart rate
)

executor = ThreadPoolExecutor(max_workers=4)


#mode
IS_TESTING = False
status = "formal"



model = "FCNN"
name = "no3P"
who = "dean"
error_list = [10, 17, 25]
align = False
use_rate = True
image_counter = 0
client_timers = {}
client_active = {}
client_processes = {}
image_queue = LightQueue()
is_processing = False



# loggin init
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"[INFO] 現在是IS_TESTING:{IS_TESTING}狀態")




def on_keypoint_done(results):
    logging.info("[INFO] on_keypoint_done")
    keyframes = keyframe_extraction(results)
    on_keyframes_done(keyframes)


def on_keyframes_done(keyframes):
    logging.info("[INFO] on_keyframes_done")
    if isinstance(keyframes, str):
        logging.warning(f"[ERROR] keyframe Error: {keyframes}")
        socketio.emit('response3', {'success': False, 'error': keyframes})
        return
    
    def pose_callback(pose_result):
        
        try:
            if isinstance(pose_result, str):
                raise Exception(pose_result)
            
           
            image_set = correct(pose_result, error, align, status)
            images_to_send = tobase64(image_set)
            
            
            socketio.emit('response3', {'success': True, 'images': images_to_send})
            logging.info("[INFO] response3 send!")
        except Exception as e:
            logging.error(f"[ERROR] Pose Recognition Error: {str(e)}", exc_info=True)
            socketio.emit('response3', {'success': False, 'error': str(e)})
    

    pose_recognition(keyframes, pose_callback)



def save_image(img_bytes, img_path):
    """同步函數：保存圖片到指定路徑"""
    try:
        # 將 bytes 轉換為 OpenCV 格式
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 創建目錄（如果不存在）
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        
        # 保存圖片
        cv2.imwrite(img_path, img)
        logging.info(f"[INFO] 圖片已保存至 {img_path}")
    except Exception as e:
        logging.error(f"[ERROR] 保存圖片失敗: {str(e)}")
    finally:
        del img
        gc.collect()


def save_image_worker():
    """背景任務：持續從佇列中取出圖片並保存"""
    while True:
        img_bytes, img_path = image_queue.get()
        save_image(img_bytes, img_path)





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
    client_sid = request.sid
    client_processes[client_sid] = None  

    def emit_periodically(sid):
        while True:
            try:
                socketio.emit('response4', {'success': True}, to=sid)
                logging.info(f"[heart rate] send response4 to {sid}")
                eventlet.sleep(1)
            except Exception as e:
                logging.error(f"heart rate error: {e}")
                break

    
    task = socketio.start_background_task(emit_periodically, client_sid)
    client_timers[client_sid] = task
    
    
    

    

@socketio.on('disconnect')
def handle_disconnect():
    client_sid = request.sid
    logging.info(f"client: {client_sid} disconnect")

    
    if client_sid in client_timers:
        task = client_timers[client_sid]
        task.kill()  
        del client_timers[client_sid]


    if client_sid in client_processes and client_processes[client_sid]:
        client_processes[client_sid].terminate()
        del client_processes[client_sid]
"""




@socketio.on('transfer')
def handleImage(data):
    global image_counter, transfer_timer, client_sid, status
    client_sid = request.sid
    
    
    if  IS_TESTING:
        status = "test"
    else:
        status = "formal"
    
    
    try:

        if "message" in data and "first" in data:
            
            base64_img = data["message"]
            first = data["first"]
            
            
            
            img_data = base64.b64decode(base64_img)  #to base64
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # to OpenCV (bgr)
           
                
            
            if first:
                
                
                if os.path.exists("formal/tmp_obj"):
                    shutil.rmtree("formal/tmp_obj")
                if os.path.exists("formal/analyze"):
                    shutil.rmtree("formal/analyze") 
                os.makedirs("formal/tmp_obj", exist_ok=True)
                os.makedirs("formal/analyze", exist_ok=True)
                
                
                cv2.imwrite("formal/tmp_obj/first.jpg", img)
                h, w, c = img.shape
                
                
                def sent_response1(result):
                    
                    if result["success"]:
                        IN = result["in_image"]
                        if socketio.server.manager.is_connected(client_sid, namespace='/'):
                            socketio.emit('response1', {'success': IN}, to=None, namespace='/')
                            logging.info(f"[INFO] IN: {IN}")
                            logging.info("[INFO] response1 finished")
                        else:
                            logging.warning(f"Client {client_sid} discoonected， response1 failed")
                    else:
                        logging.error(f"[INFO] {result['error']}")
                    
               
                input_path = f"D:/my_project/android-camera-socket-stream-master/server/{status}/tmp_obj/first.jpg"
               
                image_counter = 0
                #(function, int, int, str, callback)
                eventlet.spawn(
                    object_detection, w, h, input_path, sent_response1
                )


            else:
                #start taking pictures
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                _, buffer = cv2.imencode('.jpg', img)
                img_bytes = buffer.tobytes()
                
                img_path = f"formal/analyze/{image_counter}.jpg"
                image_queue.put((img_bytes, img_path))
                image_counter += 1
                
                

                
                
    except Exception as e:
        logging.error(f"[ERROR] {e}")




#拍攝圖片處理
@socketio.on('analyze')
def analyze(msg):
    global error, is_processing
    
    if is_processing:
        logging.warning("[INFO] processing now, refused request")
        return
    is_processing = True
    
    logging.info('[INFO] analyze get')

        
    try:
        error = error_list[int(msg)-1]
        input_path = f"D:/my_project/android-camera-socket-stream-master/server/{status}/analyze"
        executor.submit(keypoint_detection_batch, input_path, on_keypoint_done)
        logging.info("[INFO] response3 send!")
        logging.info(f"[INFO] error: {error}")
    except Exception as e:
        logging.error(f"[ERROR] response3 Error: {e}")
        socketio.emit('response3', {'success': False, 'error': str(e)})
    finally:
        is_processing = False
        



if __name__ == '__main__':
    # Start the image-saving coroutine worker
    socketio.start_background_task(save_image_worker)
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        log_output=True,  
    )


    