package com.example.skinscannerapp.ui.camera

import android.graphics.Bitmap
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Camera
import androidx.compose.material.icons.filled.FlipCameraAndroid
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import kotlinx.coroutines.launch

/**
 * Ekran kamery do robienia zdjęć skóry
 * Intuicyjny UI z podglądem i przyciskiem robienia zdjęcia
 */
@Composable
fun CameraScreen(
    onPhotoTaken: (Bitmap) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val scope = rememberCoroutineScope()
    val density = LocalDensity.current

    val cameraManager = remember { CameraManager(context) }
    var isCapturing by remember { mutableStateOf(false) }
    var previewSize by remember { mutableStateOf(IntSize.Zero) }
    
    // Rozmiar ramki w px
    val frameSizeDp = 250.dp
    val frameSizePx = with(density) { frameSizeDp.toPx().toInt() }

    DisposableEffect(Unit) {
        onDispose {
            cameraManager.shutdown()
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(Color.Black)
    ) {
        // Podgląd kamery
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    // FIT_CENTER - podgląd będzie proporcjonalny do zdjęcia!
                    scaleType = PreviewView.ScaleType.FIT_CENTER
                    scope.launch {
                        cameraManager.startCamera(lifecycleOwner, this@apply)
                    }
                }
            },
            modifier = Modifier
                .fillMaxSize()
                .onSizeChanged { size ->
                    previewSize = size
                }
        )

        // Ramka pomocnicza - pokazuje gdzie umieścić zmianę skórną
        Box(
            modifier = Modifier
                .align(Alignment.Center)
                .size(frameSizeDp)
                .border(
                    width = 3.dp,
                    color = Color.White,
                    shape = RoundedCornerShape(16.dp)
                )
        )

        // Tekst pomocy
        Text(
            text = "Umieść zmianę skórną w ramce",
            color = Color.White,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .padding(top = 100.dp)
                .background(
                    Color.Black.copy(alpha = 0.5f),
                    RoundedCornerShape(8.dp)
                )
                .padding(horizontal = 16.dp, vertical = 8.dp)
        )

        // Przyciski na dole
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.BottomCenter)
                .padding(bottom = 48.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Przycisk anulowania
            TextButton(
                onClick = onCancel
            ) {
                Text(
                    text = "Anuluj",
                    color = Color.White
                )
            }

            // Główny przycisk robienia zdjęcia
            IconButton(
                onClick = {
                    if (!isCapturing && previewSize != IntSize.Zero) {
                        isCapturing = true
                        scope.launch {
                            // Przekaż rozmiar ekranu i ramki do kadrowania
                            val photo = cameraManager.takePhoto(
                                previewWidth = previewSize.width,
                                previewHeight = previewSize.height,
                                frameSize = frameSizePx
                            )
                            isCapturing = false
                            photo?.let { onPhotoTaken(it) }
                        }
                    }
                },
                modifier = Modifier
                    .size(72.dp)
                    .clip(CircleShape)
                    .background(Color.White)
            ) {
                if (isCapturing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(32.dp),
                        color = MaterialTheme.colorScheme.primary
                    )
                } else {
                    Icon(
                        imageVector = Icons.Default.Camera,
                        contentDescription = "Zrób zdjęcie",
                        modifier = Modifier.size(36.dp),
                        tint = Color.Black
                    )
                }
            }

            // Placeholder dla symetrii
            Spacer(modifier = Modifier.width(64.dp))
        }
    }
}
