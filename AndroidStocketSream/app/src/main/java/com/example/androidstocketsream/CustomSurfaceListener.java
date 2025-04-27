package com.example.androidstocketsream;

import android.graphics.SurfaceTexture;
import android.os.Handler;
import android.util.Log;
import android.view.TextureView;
import android.os.Looper;

public class CustomSurfaceListener implements TextureView.SurfaceTextureListener {

    protected CameraHandler cameraHandler;
    protected SocketStream socketStream;
    protected TextureView textureView;
    protected int interval = 120;
    protected VoiceHandler voiceHandler;
    private MainActivity mainActivity;
    private Handler handler;
    private boolean first_handle = true;


    public CustomSurfaceListener(MainActivity mainActivity, CameraHandler cameraHandler, VoiceHandler voiceHandler,TextureView textureView) {
        this.mainActivity = mainActivity;
        this.cameraHandler = cameraHandler;
        this.textureView = textureView;
        this.voiceHandler = voiceHandler;
        this.socketStream = StateSingleton.getInstance().getSocketStream();
        this.handler = new Handler(Looper.getMainLooper());
    }

    @Override
    public void onSurfaceTextureAvailable(SurfaceTexture surfaceTexture, int i, int i1) {
        this.cameraHandler.openCamera();
    }

    @Override
    public void onSurfaceTextureSizeChanged(SurfaceTexture surfaceTexture, int i, int i1) { }

    @Override
    public boolean onSurfaceTextureDestroyed(SurfaceTexture surfaceTexture) {
        return false;
    }



    @Override
    public void onSurfaceTextureUpdated(SurfaceTexture surfaceTexture) {
        // check if the bytes should be transfered
        //這一塊會一直運行

        if (!StateSingleton.getInstance().waitInterval && StateSingleton.getInstance().runScanning) {
            if (StateSingleton.getInstance().first) {
                //first time

                //wait for feeback
                StateSingleton.getInstance().waitInterval = true;

                //Log.d(StateSingleton.getInstance().TAG, "onSurfaceTextureUpdated first=true");

                //take picture & pass to python for objection detection, this process run in main thread
                new SocketThread(this.textureView, this.socketStream).run();

                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        if (socketStream.isSuccessResponse_connect()) {

                            //person doesn't out of image
                            if (socketStream.isSuccessResponse_bbox()) {
                                Log.d(StateSingleton.getInstance().TAG, "Operation was successful!");
                                StateSingleton.getInstance().first = false;

                                voiceHandler.playAudioByNumber(21); // 播放 raw21.mp3
                                Log.d(StateSingleton.getInstance().TAG, "raw21");

                                // 停止等待
                                StateSingleton.getInstance().waitInterval = false;

                                // raw21.mp3 播放后，继续扫描
                                Log.d(StateSingleton.getInstance().TAG, "onSurfaceTextureUpdated first end");

                                // 线程计数归零
                                StateSingleton.getInstance().setThreadCount(0);
                            }
                            //not in image
                            else {
                                Log.d(StateSingleton.getInstance().TAG, "out of image");

                                //fail in first photo
                                StateSingleton.getInstance().first = true;

                                //ask to redo
                                voiceHandler.playAudioByNumber(20);
                                StateSingleton.getInstance().runScanning = false;
                            }
                        }
                         else{
                            Log.d(StateSingleton.getInstance().TAG, "connect failed!");

                            //fail in first photo
                            StateSingleton.getInstance().first = true;

                            //ask to redo
                            voiceHandler.playAudioByNumber(22);
                            StateSingleton.getInstance().runScanning = false;
                        }
                    }
                }, 5000); // 延遲 4000 毫秒 (4 秒)
            }else {
                //after first time


                //for time out stop
                if (first_handle){
                    first_handle = false;
                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            // 檢查是否還在 scanning 中
                            if (StateSingleton.getInstance().runScanning) {
                                Log.d(StateSingleton.getInstance().TAG, "Timeout reached, calling checkAllThreadsCompleted()");
                                StateSingleton.getInstance().runScanning = false;
                                mainActivity.stopscan_2main2();
                                first_handle = true;
                            }
                        }
                    }, 5 *60 * 1000); // 5分鐘 = 5 * 60 * 1000 毫秒
                }




                //generate subthread
                StateSingleton.getInstance().waitInterval = true;


                //start to take second, third photo
                StateSingleton.getInstance().started = true;


                // 启动线程并增加计数器socketThread.start();
                StateSingleton.getInstance().incrementThreadCount();
                Log.d(StateSingleton.getInstance().TAG, "thread count:"+StateSingleton.getInstance().getThreadCount());


                Thread socketThread = new Thread(new SocketThread(this.textureView, this.socketStream));
                socketThread.start();


                // 線程完成後執行計數器遞減邏輯
                socketThread.setUncaughtExceptionHandler((thread, throwable) -> {
                    StateSingleton.getInstance().decrementThreadCount();
                });




                new Handler().postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        StateSingleton.getInstance().waitInterval = false;
                    }
                }, interval);
            }
        } else if (StateSingleton.getInstance().started && !StateSingleton.getInstance().runScanning && !StateSingleton.getInstance().first) {
            checkAllThreadsCompleted();


        }

    }



    // 檢查所有線程是否完成並播放語音
    private void checkAllThreadsCompleted() {
        Log.d(StateSingleton.getInstance().TAG, "final thread count:"+StateSingleton.getInstance().getThreadCount());
        if (StateSingleton.getInstance().areAllThreadsComplete()) {
            new Thread(() -> {
                StateSingleton.getInstance().started = false;
                socketStream.attemptSend3(true);
            }).start(); // 👉 括號合起來之後才 .start()
        }
    }


}