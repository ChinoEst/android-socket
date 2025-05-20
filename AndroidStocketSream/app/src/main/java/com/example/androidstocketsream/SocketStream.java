package com.example.androidstocketsream;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.util.Base64;
import android.os.Looper;
import android.os.Handler;
import android.content.Context;
import java.util.Arrays;



import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;







import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;


import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;


public class SocketStream {

    /*
        Handles the communication with the REST-Socket
     */
    private static final String url = "http://140.116.245.200:65501";

    private Socket mSocket;
    private final List <Bitmap> imageList = new ArrayList<>(); // 存圖片名稱與 Bitmap
    private OnImagesReadyCallback onImagesReadyCallback; // 回調接口
    private final Object successLock = new Object();
    private final AtomicBoolean successResponse_bbox = new AtomicBoolean(false);
    private final AtomicBoolean successResponse_connect = new AtomicBoolean(false);
    //private final AtomicBoolean successResponse2 = new AtomicBoolean(false);
    private final AtomicBoolean successResponse3 = new AtomicBoolean(false);
    private final AtomicBoolean Response3_finish = new AtomicBoolean(false);
    private final Context context;  //

    public static SocketStream getInstance(Context context) {
        if (StateSingleton.getInstance().getSocketStream() == null) {
            SocketStream socketStream = new SocketStream(context.getApplicationContext());
            StateSingleton.getInstance().setSocketStream(socketStream);
        }
        return StateSingleton.getInstance().getSocketStream();
    }


    private SocketStream(Context context) {
        Log.d("SocketStream", "Constructor called");
        this.context = context.getApplicationContext();
        try {
            IO.Options options = new IO.Options();
            options.transports = new String[] {"websocket"};
            mSocket = IO.socket(url, options);


            mSocket.on("response1", onResponse1);
            //mSocket.on("response2", onResponse2);
            mSocket.on("response3", onResponse3);
            mSocket.on("response4", onResponse4);


            // 新增通用 listener 註冊
            String[] genericEvents = new String[]{
                    "response1", "response2", "response3", "disconnect", "connect_error", "error", "yourCustomEvent"
            };
            for (String event : genericEvents) {
                addGenericListener(event);
            }

            mSocket.connect();
        } catch (Exception e) {
            Log.e(StateSingleton.getInstance().TAG, "SocketStream connection error!", e);
        }
    }

    public boolean isConnected() {
        return mSocket != null && mSocket.connected();
    }


    // 加入通用 listener
    private void addGenericListener(String eventName) {
        mSocket.on(eventName, args -> {
            Log.d(StateSingleton.getInstance().TAG, "🟡 Generic listener triggered: " + eventName);
            if (args.length > 0) {
                for (Object arg : args) {
                    Log.d(StateSingleton.getInstance().TAG, "📝 Data: " + arg.toString());
                }
            }
        });
    }



    // for bbox return
    // for bbox return
    private final Emitter.Listener onResponse1 = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            Log.d(StateSingleton.getInstance().TAG, "onResponse1 get");
            if (args.length > 0) {
                // 提取服务端传回的数据

                JSONObject data = (JSONObject) args[0];

                if (data.has("success")) {
                    successResponse_connect.set(true);
                    successResponse_bbox.set(((org.json.JSONObject) args[0]).optBoolean("success", false));
                    Log.d(StateSingleton.getInstance().TAG, "Response1 success:: " + successResponse_bbox.get());
                }

            }
        }
    };


    /*
    private final Emitter.Listener onResponse2 = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            Log.d(StateSingleton.getInstance().TAG, "onResponse2 get");
            if (args.length > 0) {
                // 提取服务端传回的数据

                JSONObject data = (JSONObject) args[0];

                if (data.has("message")) {
                    String msg = data.optString("message");
                    if ("All images received".equals(msg)) {
                        Log.d(StateSingleton.getInstance().TAG, " All images are received! Ready to analyze.");
                        setSuccessResponse2(true);
                    }
                }

            }
        }
    };

     */



    private final Emitter.Listener onResponse3 = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            if (args.length > 0) {
                try {
                    JSONObject jsonResponse = (JSONObject) args[0];
                    successResponse3.set(jsonResponse.optBoolean("success", false));
                    Log.d(StateSingleton.getInstance().TAG, "Response3 success " + successResponse3.get());
                    // 根据布尔值做进一步的处理
                    if (successResponse3.get()) {

                        //server process sucess
                        Log.d(StateSingleton.getInstance().TAG, "Response3 operation was successful!");

                        // 解析并存储 Base64 图片
                        JSONArray imagesArray = jsonResponse.optJSONArray("images");
                        if (imagesArray != null) {
                            imageprocess(imagesArray);
                            if (onImagesReadyCallback != null) {
                                new Handler(Looper.getMainLooper()).post(() ->
                                        onImagesReadyCallback.onImagesReady(imageList)
                                );
                                Log.d(StateSingleton.getInstance().TAG, "onImagesReadyCallback success");
                            }
                        }
                    }
                } catch (Exception e) {
                    Log.e(StateSingleton.getInstance().TAG, "Error processing response3: " + e.getMessage(), e);
                }
            }
            setResponse3_finish(true);
        }
    };


    //use for check Listener working

    private final Emitter.Listener onResponse4 = new Emitter.Listener() {
        @Override
        public void call(Object... args) {
            Log.d(StateSingleton.getInstance().TAG, "test onResponse4 get");
        }
    };




    //處理接收的圖片
    private void imageprocess(JSONArray imagesArray){
        try{
            for (int i = 0; i < imagesArray.length(); i++) {
                JSONObject imageObject = imagesArray.getJSONObject(i);
                String base64Image = imageObject.getString("data");

                Bitmap bitmap = decodeBase64ToBitmap(base64Image);
                if (bitmap != null) {
                    imageList.add(bitmap);
                }
                Log.d(StateSingleton.getInstance().TAG, "img " + i + " finish");
            }
        }catch (JSONException e) {
            Log.e(StateSingleton.getInstance().TAG, "Error processing images: " + e.getMessage(), e);
        }

    }


    // 获取图片列表
    public List<Bitmap> getImageList() {
        return imageList;
    }

    // 添加設置回調的方法
    public void setOnImagesReadyCallback(OnImagesReadyCallback callback) {
        this.onImagesReadyCallback = callback;
    }



    public interface OnImagesReadyCallback {
        void onImagesReady(List<Bitmap> images);
    }


    //send photos we take to server
    public void attemptSend(byte[] message) {
        try {
            //pass picture and connection status
            JSONObject data = new JSONObject();
            data.put("message", Base64.encodeToString(message, Base64.DEFAULT));
            data.put("first", StateSingleton.getInstance().first);
            mSocket.emit("transfer", data);
            Log.e(StateSingleton.getInstance().TAG,"link");

        } catch (Exception e) {
            Log.e(StateSingleton.getInstance().TAG, "SocketStream runs on an error while sending the bytes to the socket server!");
        }
    }


    public void attemptSend2(String message) {
        try {
            mSocket.emit("transfer", message);
        } catch (Exception e) {
            Log.e(StateSingleton.getInstance().TAG, "SocketStream runs on an error while sending the bytes to the socket server!");
        }
    }


    //send difficult and ask analyze start
    public void attemptSend3(boolean value) {
        try {
            // 将布尔值直接发送
            mSocket.emit("analyze", StateSingleton.getInstance().difficult);
            Log.d(StateSingleton.getInstance().TAG, "Boolean value sent to server: " + value);
        } catch (Exception e) {
            Log.e(StateSingleton.getInstance().TAG, "SocketStream encountered an error while sending a boolean to the server!", e);
        }
    }


    private Bitmap decodeBase64ToBitmap(String base64Str) {
        try {
            byte[] decodedBytes = Base64.decode(base64Str, Base64.DEFAULT);
            return BitmapFactory.decodeByteArray(decodedBytes, 0, decodedBytes.length);
        } catch (IllegalArgumentException e) {
            Log.e(StateSingleton.getInstance().TAG, "Base64 decoding error: " + e.getMessage(), e);
            return null;
        }
    }

    public void clearImageList() {
        imageList.clear();
    }

    public boolean isSuccessResponse_bbox() {
        return successResponse_bbox.get();
    }
    public boolean isSuccessResponse_connect() {
        return successResponse_connect.get();
    }

    /*
    public boolean isSuccessResponse2() {
        return successResponse2.get();
    }


     */

    public boolean isSuccessResponse3() {
        return successResponse3.get();
    }

    public boolean isResponse3_finish() {
        return Response3_finish.get();
    }

    public void setSuccessResponse_bbox(boolean received) {
        this.successResponse_bbox.set(received);
    }
    public void setSuccessResponse_connect(boolean received) {
        this.successResponse_connect.set(received);
    }

    /*
    public void setSuccessResponse2(boolean received) {
        this.successResponse2.set(received);
    }
     */

    public void setSuccessResponse3(boolean received) {
        this.successResponse3.set(received);
    }
    public void setResponse3_finish(boolean received) {
        this.Response3_finish.set(received);
    }
    /*
    public void re(){
        Log.d(StateSingleton.getInstance().TAG, "disconnect!");
        mSocket.off("response1", onResponse1);
        mSocket.off("response2", onResponse2);
        mSocket.off("response3", onResponse3);
        mSocket.off("response4", onResponse4);
        mSocket.disconnect();
        Log.d(StateSingleton.getInstance().TAG, "connect!");
        mSocket.on("response1", onResponse1);
        mSocket.on("response2", onResponse2);
        mSocket.on("response3", onResponse3);
        mSocket.on("response4", onResponse4);
        mSocket.connect();
    }

     */

}


