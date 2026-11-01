package com.swin.android

import android.app.Activity
import android.os.Bundle
import android.content.Context
import android.content.Intent
import android.media.projection.MediaProjectionManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {

    private lateinit var status: TextView
    private var permissionGranted = false

    companion object {
        private const val REQUEST_CODE = 1001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(40, 60, 40, 40)
        }

        val title = TextView(this).apply {
            text = "SWIN ANDROID"
            textSize = 28f
        }

        status = TextView(this).apply {
            text = "Устройство готово"
            textSize = 18f
            setPadding(0, 30, 0, 30)
        }

        val startButton = Button(this).apply {
            text = "START"
            setOnClickListener {
                val manager = getSystemService(
                    Context.MEDIA_PROJECTION_SERVICE
                ) as MediaProjectionManager

                startActivityForResult(
                    manager.createScreenCaptureIntent(),
                    REQUEST_CODE
                )
            }
        }

        val settingsButton = Button(this).apply {
            text = "SETTINGS"
            setOnClickListener {
                status.text = "Настройки приложения"
            }
        }

        layout.addView(title)
        layout.addView(status)
        layout.addView(startButton)
        layout.addView(settingsButton)

        setContentView(layout)
    }

    @Deprecated("Deprecated in Android")
    override fun onActivityResult(
        requestCode: Int,
        resultCode: Int,
        data: Intent?
    ) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == REQUEST_CODE) {
            permissionGranted = resultCode == RESULT_OK

            status.text = if (permissionGranted) {
                "Разрешение получено"
            } else {
                "Разрешение отклонено"
            }
        }
    }
}
