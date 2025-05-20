from concurrent.futures import ThreadPoolExecutor
import requests
import logging

# 全局線程池（與 server.py 共用）
executor = ThreadPoolExecutor(max_workers=4)

def keypoint_detection_batch(dir_path, callback):
    
    def async_task():
        try:
            logging.info("keypoint detection start!")
            response = requests.post(
                f"http://localhost:8000/predict_batch?dir_path={dir_path}"
            )
            response.raise_for_status()
            result = response.json().get("results", {})
            logging.info("keypoint detection finished!")
            
            callback(result)
        except Exception as e:
            callback(str(e))
            logging.info(f"keypoint detection error {str(e)}")
    
    # 提交到全局線程池
    executor.submit(async_task)
