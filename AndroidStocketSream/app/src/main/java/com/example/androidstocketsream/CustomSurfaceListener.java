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
    protected int interval = 135;
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

                                // stop waiting
                                StateSingleton.getInstance().waitInterval = false;


                                Log.d(StateSingleton.getInstance().TAG, "onSurfaceTextureUpdated first end");


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

                                handler.postDelayed(new Runnable() {
                                    @Override
                                    public void run() {
                                        StateSingleton.getInstance().runScanning = true;
                                        StateSingleton.getInstance().waitInterval = false;
                                        Log.d(StateSingleton.getInstance().TAG, "restarted");
                                    }
                                }, 10000);//after 10s, scan again


                            }
                        }
                         else{
                            Log.d(StateSingleton.getInstance().TAG, "connect failed!");

                            //fail in first photo
                            StateSingleton.getInstance().first = true;

                            //ask to reconnect
                            voiceHandler.playAudioByNumber(22);
                            StateSingleton.getInstance().runScanning = false;
                        }
                    }
                }, 6000); //afer raw1 play
            }else {
                //after first time


                //for time out stop
                if (first_handle){
                    first_handle = false;
                    new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            // check still in scanning
                            if (StateSingleton.getInstance().runScanning) {
                                Log.d(StateSingleton.getInstance().TAG, "Timeout reached, calling checkAllThreadsCompleted()");
                                StateSingleton.getInstance().runScanning = false;
                                mainActivity.stopscan_2main2();
                                first_handle = true;
                            }
                        }
                    }, 5 *60 * 1000); // after 5 mins , stop by itself
                }



                StateSingleton.getInstance().waitInterval = true;


                //start to take second, third photo
                StateSingleton.getInstance().started = true;


                // count number of threads
                StateSingleton.getInstance().incrementThreadCount();
                Log.d(StateSingleton.getInstance().TAG, "thread count:"+StateSingleton.getInstance().getThreadCount());

                //generate new thread to get photo
                Thread socketThread = new Thread(new SocketThread(this.textureView, this.socketStream) {
                    @Override
                    public void run() {
                        try {
                            super.run();  // 執行原本的 run()
                        } finally {
                            StateSingleton.getInstance().decrementThreadCount();
                            Log.d(StateSingleton.TAG, "thread count decremented");
                        }
                    }
                });
                socketThread.start();

                //stop for a while
                new Handler().postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        StateSingleton.getInstance().waitInterval = false;
                    }
                }, interval);
            }
        } else if (StateSingleton.getInstance().started && !StateSingleton.getInstance().runScanning && !StateSingleton.getInstance().first) {
            //finish all of thread
            checkAllThreadsCompleted();


        }

    }



    // after all of thread finish,
    private void checkAllThreadsCompleted() {
        Log.d(StateSingleton.getInstance().TAG, "final thread count:"+StateSingleton.getInstance().getThreadCount());
        if (StateSingleton.getInstance().areAllThreadsComplete()) {

            StateSingleton.getInstance().started = false;
            //send analyze
            //socketStream.attemptSend3(true);
        }
    }


}