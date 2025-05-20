package com.example.androidstocketsream;

import java.util.concurrent.atomic.AtomicInteger;

public class StateSingleton {

    // Singleton for the state management
    public static boolean waitInterval = false;  //If True, stop taking a photo for a while
    public static boolean runScanning = false;  //If True, respresent for be taking  pictures which are after first photo
    public static boolean first = true;  // If True,  taking a photo for bbox
    public static boolean started = false;
    public static boolean raw1_end = false;
    public static int difficult = 1; // 1:easy 2:medium 3:hard
    public static final String TAG = "AndroidSocketStream";


    // 用于追踪活动线程数
    private final AtomicInteger threadCount = new AtomicInteger(0);

    // SocketStream 实例
    private SocketStream socketStream;

    private static StateSingleton INSTANCE = null;

    private StateSingleton() {};

    public static StateSingleton getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new StateSingleton();
        }
        return(INSTANCE);
    }

    // 获取线程计数器
    public AtomicInteger getThreadCount() {
        return threadCount;
    }





    public void incrementThreadCount() {
        threadCount.incrementAndGet();
    }



    public int decrementThreadCount() {
        return threadCount.decrementAndGet();
    }






    public boolean areAllThreadsComplete() {
        return threadCount.get() == 0;
    }





    //歸0
    public void setThreadCount(int value) {
        threadCount.set(value);
    }


    /**
     * 获取 SocketStream
     */
    public SocketStream getSocketStream() {
        return socketStream;
    }

    /**
     * 设置 SocketStream
     */
    public void setSocketStream(SocketStream socketStream) {
        this.socketStream = socketStream;
    }


    public void reset() {
        first = true;
        runScanning = false;
        waitInterval = false;
        started = false;
        raw1_end = false;
        difficult = 1;


        // 重設線程計數器
        threadCount.set(0);

        if (socketStream != null) {
            socketStream.clearImageList(); // 需要在 SocketStream 里实现此方法
        }

        // 清除 callback 或 listener（避免 memory leak）
        if (socketStream != null) {
            socketStream.setOnImagesReadyCallback(null);
        }

        // 重設 Response 狀態
        socketStream.setSuccessResponse_bbox(false);
        socketStream.setSuccessResponse_connect(false);
        socketStream.setSuccessResponse3(false);
        socketStream.setResponse3_finish(false);
        //socketStream.setSuccessResponse2(false);

        first = true;
        runScanning = false;
    }

}