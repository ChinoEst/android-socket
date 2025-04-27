package com.example.androidstocketsream;

import android.content.Context;
import android.media.MediaPlayer;

public class VoiceHandler {
    private MediaPlayer mediaPlayer;
    private Context context;

    public VoiceHandler(Context context) {
        this.context = context.getApplicationContext();
    }

    /**
     * 播放本地音檔（根據數字決定 raw 資源）
     *
     * @param number 數字，例如 1 對應 raw1，2 對應 raw2，依此類推
     */
    public void playAudioByNumber(int number) {
        if (mediaPlayer != null) {
            mediaPlayer.release(); // 釋放上一次的資源
        }

        // 動態獲取 raw 資源 ID
        String resourceName = "raw" + number; // 拼接資源名稱，例如 raw1, raw2
        int resId = context.getResources().getIdentifier(resourceName, "raw", context.getPackageName());

        if (resId == 0) {
            // 如果找不到對應的音檔，則提示
            throw new IllegalArgumentException("無效的音檔名稱：" + resourceName);
        }

        mediaPlayer = MediaPlayer.create(context, resId);

        if (mediaPlayer != null) {
            mediaPlayer.setOnCompletionListener(mp -> {
                mediaPlayer.release(); // 播放完釋放資源
                mediaPlayer = null;
            });
            mediaPlayer.start();
        }
    }

    /**
     * 停止播放音檔
     */
    public void stopAudio() {
        if (mediaPlayer != null && mediaPlayer.isPlaying()) {
            mediaPlayer.stop();
            mediaPlayer.release();
            mediaPlayer = null;
        }
    }

    /**
     * 釋放資源
     */
    public void release() {
        if (mediaPlayer != null) {
            mediaPlayer.release();
            mediaPlayer = null;
        }
    }
}
