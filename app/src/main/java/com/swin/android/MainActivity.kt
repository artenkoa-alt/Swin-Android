package com.swin.android

import android.app.Activity
import android.app.AlertDialog
import android.media.projection.MediaProjectionManager
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var status: TextView
    private lateinit var startButton: Button

    private var permissionGranted = false

    private val screenPermission =
        registerForActivityResult(
            ActivityResultContracts.StartActivityForResult()
        ) { result ->

            if (result.resultCode == Activity.RESULT_OK) {
                permissionGranted = true
                status.text =
                    "Разрешение получено. Демонстрация пока не запущена."
                startButton.text = "STOP"
            } else {
                permissionGranted = false
                status.text = "Разрешение не предоставлено."
            }
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

        startButton = Button(this).apply {
            text = "START"
            setOnClickListener {
                if (!permissionGranted) {
                    val manager =
                        getSystemService(MEDIA_PROJECTION_SERVICE)
                            as MediaProjectionManager

                    screenPermission.launch(
                        manager.createScreenCaptureIntent()
                    )
                } else {
                    permissionGranted = false
                    status.text = "Сеанс остановлен."
                    startButton.text = "START"
                }
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
}
