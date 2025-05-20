from concurrent.futures import ThreadPoolExecutor
import requests
import logging

# 全局線程池（與 server.py 共用）
executor = ThreadPoolExecutor(max_workers=4)

def pose_recognition(keyframes, callback):

    def async_task():
        try:
            logging.info("pose_recognition start!")
            print(f"[INFO] keyframe type:{type(keyframes)}")
            response = requests.post(
                "http://localhost:8001/predict",
                json=keyframes)

            response.raise_for_status()
            logging.info("[INFO] pose_recognition")
            callback(response.json())
        except requests.exceptions.RequestException as re:
            error_msg = f"[ERROR] API requests fail: {str(re)}"
            logging.error(error_msg)
            callback({"error": error_msg})
        except Exception as e:
            error_msg = f"[ERROR] pose_recognition error: {str(e)}"
            logging.error(error_msg, exc_info=True)
            callback({"error": error_msg})
    
    # 提交到線程池
    executor.submit(async_task)
