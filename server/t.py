import eventlet
from eventlet import tpool
from eventlet.hubs import get_hub

def callback(data):
    print("callback 被呼叫，資料：", data)

def async_task():
    print("async_task 執行完，準備呼叫 callback")
    get_hub().schedule_call_global(0, callback, {"hello": "world"})

if __name__ == "__main__":
    eventlet.monkey_patch()
    tpool.execute(async_task)
    eventlet.sleep(5)
