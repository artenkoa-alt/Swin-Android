package com.swin.android

import android.app.Activity
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(32, 32, 32, 32)
            setBackgroundColor(Color.rgb(15, 18, 28))
        }

        val title = TextView(this).apply {
            text = "SWIN ANDROID"
            textSize = 28f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
        }

        val status = TextView(this).apply {
            text = "Отключено"
            textSize = 16f
            setTextColor(Color.LTGRAY)
            gravity = Gravity.CENTER
        }

        val start = Button(this).apply {
            text = "START"
            setOnClickListener {
                status.text = "Ожидание разрешения пользователя"
            }
        }

        val settings = Button(this).apply {
            text = "SETTINGS"
            setOnClickListener {
                status.text = "Настройки приложения"
            }
        }

        layout.addView(title)
        layout.addView(status)
        layout.addView(start)
        layout.addView(settings)

        setContentView(layout)
    }
}
