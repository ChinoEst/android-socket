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

        // set ViewPager2
        adapter = new ImagePagerAdapter(new ArrayList<>()); //
        viewPager.setAdapter(adapter);

        // get SocketStream
        SocketStream socketStream = StateSingleton.getInstance().getSocketStream();
        Log.d(StateSingleton.getInstance().TAG, "after socketStream");

        if (socketStream != null) {
            // if photo exists, update
            if (!socketStream.getImageList().isEmpty()) {
                adapter.updateImages(socketStream.getImageList());
                Log.d(StateSingleton.getInstance().TAG, "Images updated directly from existing imageList");
            }
            //or after photo finish, update
            socketStream.setOnImagesReadyCallback(images -> runOnUiThread(() -> {
                adapter.updateImages(images);
                Log.d(StateSingleton.getInstance().TAG, "Images updated in ViewPager via callback");
            }));
        } else {
            Log.e("MainActivity2", "SocketStream is null.");
        }

        // btn to restart
        resetButton.setOnClickListener(v -> {
            resetParameters();
            Intent intent = new Intent(MainActivity2.this, MainActivity_home.class);
            startActivity(intent);
            finish();
        });

    }



    private void resetParameters() {
        StateSingleton.getInstance().reset();
    }

    @Override
    public void onBackPressed() {}
}
