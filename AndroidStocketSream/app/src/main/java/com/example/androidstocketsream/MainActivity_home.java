package com.example.androidstocketsream;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;
import android.app.Dialog;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.view.Gravity;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.ArrayAdapter;
import android.widget.ImageButton;
import android.widget.Spinner;
import android.widget.Toast;
import java.util.Arrays;


public class MainActivity_home extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home); // 绑定新的 XML 布局

        ImageButton difficultyButton = findViewById(R.id.imageButton);
        difficultyButton.setOnClickListener(v -> showDialogSetting());

        Button startButton = findViewById(R.id.button);
        startButton.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity_home.this, MainActivity.class);
            startActivity(intent);
        });


    }

    @Override
    public void onBackPressed() {
        new android.app.AlertDialog.Builder(this)
                .setTitle("確定要離開嗎？")
                .setMessage("按下「確定」將結束應用程式。")
                .setPositiveButton("確定", (dialog, which) -> {
                    super.onBackPressed(); // 真的退出
                })
                .setNegativeButton("取消", null)
                .show();
        // 停用返回鍵，不執行任何操作
    }

    private void showDialogSetting() {
        Dialog dialog = new Dialog(this);
        dialog.setContentView(R.layout.dialog_setting);
        Window window = dialog.getWindow();
        if (window != null) {
            window.setLayout(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            window.setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            window.setGravity(Gravity.CENTER);
        }

        Spinner spinner = dialog.findViewById(R.id.spinner);
        Button btnConfirm = dialog.findViewById(R.id.btnConfirm);
        Button btnCancel = dialog.findViewById(R.id.btnCancel);

        // Spinner 選項
        String[] options = {"簡單", "普通", "困難"};

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, options);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);

        // 設定 Spinner 的預設選項
        int selectedIndex = StateSingleton.getInstance().difficult; // 獲取 difficult 的索引值
        if (selectedIndex >= 0 && selectedIndex < options.length) {
            spinner.setSelection(selectedIndex);  // 設定選中的項目
        }

        btnCancel.setOnClickListener(v -> {
            dialog.dismiss(); // 取消時不保存設定，直接關閉對話框
        });

        btnConfirm.setOnClickListener(v -> {
            String selected = spinner.getSelectedItem().toString();
            Toast.makeText(this, "你選的是: " + selected, Toast.LENGTH_SHORT).show();

            // 保存當前選擇的難度設定
            StateSingleton.getInstance().difficult = Arrays.asList(options).indexOf(selected);

            dialog.dismiss(); // 保存後關閉對話框
        });

        dialog.show();
    }
}
