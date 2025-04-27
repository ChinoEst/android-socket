package com.example.androidstocketsream;


import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Pair;
import android.widget.Button;
import android.util.Log;
import android.os.Handler;
import android.os.Looper;
import androidx.appcompat.app.AppCompatActivity;
import androidx.viewpager2.widget.ViewPager2;


import java.util.ArrayList;
import java.util.List;

public class MainActivity2 extends AppCompatActivity {

    private ViewPager2 viewPager;
    private ImagePagerAdapter adapter;
    private Button resetButton;
    private List<Pair<String, Bitmap>> imageList = new ArrayList<>();


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);

        viewPager = findViewById(R.id.viewPager);
        resetButton = findViewById(R.id.resetButton);

        // 設置 ViewPager2 的適配器
        adapter = new ImagePagerAdapter(new ArrayList<>()); // 初始化為空
        viewPager.setAdapter(adapter);

        // 取得 SocketStream 實例
        SocketStream socketStream = StateSingleton.getInstance().getSocketStream();
        Log.d(StateSingleton.getInstance().TAG, "after socketStream");

        if (socketStream != null) {
            // 設定回說，圖片處理完畢後觸發
            socketStream.setOnImagesReadyCallback(images -> runOnUiThread(() -> {
                adapter.updateImages(images); // 更新圖片
                Log.d(StateSingleton.getInstance().TAG, "Images updated in ViewPager");
            }));
        } else {
            Log.e("MainActivity2", "SocketStream is null.");
        }

        // 按鈕點擊事件：初始化變數並返回主畫面
        resetButton.setOnClickListener(v -> {
            resetParameters();
            Intent intent = new Intent(MainActivity2.this, MainActivity_home.class);
            startActivity(intent);
            finish();
        });

        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            if (socketStream != null && !socketStream.isSuccessResponse2()) {
                Log.e("MainActivity2", "No response2 received within 30 seconds");
                // 可選：顯示錯誤提示
            }
        }, 30000); // 30 秒超時
    }



    private void resetParameters() {
        StateSingleton.getInstance().reset();
    }

    @Override
    public void onBackPressed() {}
}
