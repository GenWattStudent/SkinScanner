package com.example.skinscannerapp

import android.Manifest
import android.graphics.Bitmap
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.example.skinscannerapp.ui.camera.CameraScreen
import com.example.skinscannerapp.ui.screens.HomeScreen
import com.example.skinscannerapp.ui.theme.SkinScannerAppTheme
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import com.google.accompanist.permissions.rememberPermissionState

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            SkinScannerAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    SkinScannerApp()
                }
            }
        }
    }
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun SkinScannerApp() {
    // Stan nawigacji
    var showCamera by remember { mutableStateOf(false) }
    var capturedPhoto by remember { mutableStateOf<Bitmap?>(null) }

    // Uprawnienia kamery
    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)

    if (showCamera) {
        if (cameraPermissionState.status.isGranted) {
            CameraScreen(
                onPhotoTaken = { bitmap ->
                    capturedPhoto = bitmap
                    showCamera = false
                },
                onCancel = {
                    showCamera = false
                }
            )
        } else {
            // Poproś o uprawnienia
            LaunchedEffect(Unit) {
                cameraPermissionState.launchPermissionRequest()
            }
            
            // Wróć do home jeśli odmówiono
            LaunchedEffect(cameraPermissionState.status) {
                if (!cameraPermissionState.status.isGranted) {
                    showCamera = false
                }
            }
        }
    } else {
        HomeScreen(
            onOpenCamera = {
                if (cameraPermissionState.status.isGranted) {
                    showCamera = true
                } else {
                    cameraPermissionState.launchPermissionRequest()
                    showCamera = true
                }
            },
            capturedPhoto = capturedPhoto,
            onClearPhoto = { capturedPhoto = null }
        )
    }
}