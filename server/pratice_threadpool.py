import eventlet
eventlet.monkey_patch()


from util.keypoint_detection import keypoint_detection_batch
from util.keyframe import keyframe_extraction
from util.correct import correct
from util.pose_recognition import pose_recognition
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=3)


def after_keypoint(future):
    keypoint = future.result()
    
    future = executor.submit(keyframe_extraction, result_list= keypoint)
    
    future.add_done_callback(lambda f: after_keyframe(f))
    
def after_keyframe(future):

    keyframe = future.result()

    future = excutor.submit(pose_recognition, keyframes= keyframe)
    
    future.add_done_callback(lambda f: after_recognition(f))  
    
def after_recognition(future):
    
    pose_result = future.result()
    imgs = correct(pose_result, error, align, status)
    img_to_send = to_base64(imgs)


@socketio.on('analyze')
def analyze(msg):
    error = error_list[int(msg)-1]
    
        
    future = executor.submit(keypoint_detection_batch, dir_path=msg['dir_path'])
    
    
    future.add_done_callback(lambda f: after_keypoint(f))
    
    
    
def keypoint_detection_batch(dir_path, callback):

    try:
        logging.info("keypoint detection start!")
        response = requests.post(
            f"http://localhost:8000/predict_batch?dir_path={dir_path}"
        )
        response.raise_for_status()
        result = response.json().get("results", {})
        logging.info("keypoint detection finished!")
        return result 
    except Exception as e:
        logging.info(f"Error! {str(e)}")
