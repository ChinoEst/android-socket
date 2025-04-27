package com.example.androidstocketsream;


import androidx.appcompat.app.AppCompatActivity;


import android.app.AlertDialog;
import android.os.Bundle;
import android.util.Log;
import android.view.TextureView;
import android.view.View;
import android.widget.Button;
import android.os.Handler;
import android.content.Intent;



public class MainActivity extends AppCompatActivity {

    private CameraHandler cameraHandler;
    private TextureView textureView;
    private Button startBtn;
    private Handler handler;
    private VoiceHandler voiceHandler;
    private AlertDialog loadingDialog;
    private boolean Raw1_end = false;
    private Thread checkThread;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //  SocketStream 被初始化
        initSocketStream();
        //  handler, voice, cemera 初始化
        initViews();
        //主判斷邏輯
        initListener();
    }

    private void initSocketStream(){
        if (StateSingleton.getInstance().getSocketStream() == null) {
            Log.d("MainActivity", "Initializing SocketStream...");
            SocketStream socketStream = SocketStream.getInstance(getApplicationContext());

            StateSingleton.getInstance().setSocketStream(socketStream);
        }
    }

    private void initViews(){
        textureView = findViewById(R.id.texture);
        startBtn = findViewById(R.id.btn_start);
        handler = new Handler();
        voiceHandler = new VoiceHandler(this);
        this.cameraHandler = new CameraHandler(this, getApplicationContext(), textureView);
        textureView.setSurfaceTextureListener(new CustomSurfaceListener(this, cameraHandler, voiceHandler, textureView));
    }

    private void initListener(){
        this.startBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                startBtn.setEnabled(false);

                new Handler().postDelayed(() -> startBtn.setEnabled(true), 1500);

                //開始執行拍照
                if (!StateSingleton.getInstance().runScanning){
                    startScanFlow();

                }
                else {
                    Log.d(StateSingleton.getInstance().TAG, "nothing");
                    //SocketStream socketStream = StateSingleton.getInstance().getSocketStream();
                    //close camera
                    StateSingleton.getInstance().runScanning = false;
                    //cameraHandler.closeCamera();
                    //textureView.setSurfaceTextureListener(null);
                    //socketStream.re();
                    //停止拍照，並準備跳至MainActivity2
                    stopscan_2main2();
                }
            }
        });
    }

    private void startScanFlow(){
        startBtn.setText("Stop");

        StateSingleton.getInstance().started = true;

        if (voiceHandler != null) {
            voiceHandler.playAudioByNumber(1); // 如果非空则调用
        } else {
            Log.e("MainActivity", "voiceHandler is null!");
        }

        Log.d(StateSingleton.getInstance().TAG, "handler.postDelayed1");

        // 延遲 20 秒後設置 runScanning 為 true
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                Log.d(StateSingleton.getInstance().TAG, "handler.postDelayed2");
                StateSingleton.getInstance().runScanning = true;
            }
        }, 20000); // 延遲 20000 毫秒 (20 秒)
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                Log.d(StateSingleton.getInstance().TAG, "handler.postDelayed2");
                setRaw1_end(true);
            }
        }, 24000); // 延遲 20000 毫秒 (20 秒)
    }

    public void stopscan_2main2(){
        //停止運作

        StateSingleton.getInstance().runScanning = false;
        //textureView.setSurfaceTextureListener(null);
        voiceHandler.playAudioByNumber(4);
        showLoadingDialog();

        checkThread = new Thread(() -> {
            SocketStream socketStream = StateSingleton.getInstance().getSocketStream();
            while (!socketStream.isSuccessResponse3()) {
                Log.d("SocketStatus", "Socket connected: " + socketStream.isConnected());
                try {
                    Thread.sleep(5000); // 每5秒檢查一次
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

            // 當 successResponse3 成功，切回主線程處理
            runOnUiThread(() -> {
                Log.d(StateSingleton.getInstance().TAG, "mainactivity2 start!");

                hideLoadingDialog();
                Intent intent = new Intent(MainActivity.this, MainActivity2.class);
                startActivity(intent);
            });
        });
        checkThread.start();

    }



    // 可提供 getter 和 setter 方法來存取 success 變數
    public boolean isRaw1_end() {
        return Raw1_end;
    }

    public void setRaw1_end(boolean Raw1_end) {
        this.Raw1_end = Raw1_end;
    }

    @Override
    public void onBackPressed() {}


    //open pass picture
    private void showLoadingDialog() {
        if (loadingDialog == null) {
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setView(R.layout.dialog_loading);
            builder.setCancelable(false);
            loadingDialog = builder.create();
        }
        loadingDialog.show();
    }

    //close pass picture
    private void hideLoadingDialog() {
        if (loadingDialog != null && loadingDialog.isShowing()) {
            loadingDialog.dismiss();
        }
    }

    /*
    Runnable checkRunnable = new Runnable() {
        @Override
        public void run() {
            SocketStream socketStream = StateSingleton.getInstance().getSocketStream();
            Log.d("SocketStatus", "Socket connected: " + socketStream.isConnected());
            if (socketStream.isSuccessResponse3()){
                Log.d(StateSingleton.getInstance().TAG, "mainactivity2 start!");

                hideLoadingDialog();
                Intent intent = new Intent(MainActivity.this, MainActivity2.class);//start ainactivity2
                startActivity(intent);
            }
            else{
                handler.postDelayed(this, 5000);//check every five seconds
            }
        }
    };
     */

}