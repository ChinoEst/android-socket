package com.example.androidstocketsream;

import android.graphics.Bitmap;
import android.util.Log;
import android.view.TextureView;


import java.io.ByteArrayOutputStream;

public class SocketThread implements Runnable{

    private TextureView textureView;
    private SocketStream socketStream;

    public SocketThread(TextureView textureView, SocketStream socketStream) {
        this.textureView = textureView;
        this.socketStream = socketStream;
    }

    @Override
    public void run() {
        try {
            // generate bitmap and byte array stream for the compress
            Bitmap bmp = textureView.getBitmap();
            //Log.d(StateSingleton.getInstance().TAG, "bmp1");
            ByteArrayOutputStream stream = new ByteArrayOutputStream();
            bmp.compress(Bitmap.CompressFormat.JPEG, 80, stream);

            // byte array and recycle call for better performance
            byte[] byteArray = stream.toByteArray();
            bmp.recycle();

            // send data to the flask socket server
            this.socketStream.attemptSend(byteArray);
            //Log.d(StateSingleton.getInstance().TAG, "byteArray:"+  Arrays.toString(byteArray));
        }catch(Exception e){
            Log.d(StateSingleton.getInstance().TAG, "SocketThread runs on an error!");
        }
    }


}