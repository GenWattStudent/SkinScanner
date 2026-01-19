package com.example.skinscannerapp.ui.camera

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.Matrix
import android.graphics.Rect
import android.graphics.YuvImage
import android.os.Environment
import android.util.Log
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors
import kotlin.coroutines.resume
import kotlin.coroutines.suspendCoroutine

/**
 * Manager kamery - SOLID: Single Responsibility
 * Odpowiada tylko za obsługę kamery CameraX
 */
class CameraManager(private val context: Context) {

    private var imageCapture: ImageCapture? = null
    private var cameraProvider: ProcessCameraProvider? = null
    private val cameraExecutor = Executors.newSingleThreadExecutor()

    /**
     * Inicjalizuje podgląd kamery
     */
    suspend fun startCamera(
        lifecycleOwner: LifecycleOwner,
        previewView: PreviewView
    ) = suspendCoroutine { continuation ->
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)

        cameraProviderFuture.addListener({
            cameraProvider = cameraProviderFuture.get()

            // Podgląd w najwyższej jakości
            val preview = Preview.Builder()
                .setTargetAspectRatio(AspectRatio.RATIO_4_3)
                .build()
                .also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }

            // Capture w JPEG dla najlepszej kompatybilności
            imageCapture = ImageCapture.Builder()
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
                .setTargetAspectRatio(AspectRatio.RATIO_4_3)
                .setJpegQuality(100)  // Najwyższa jakość JPEG
                .build()

            // Użyj tylnej kamery
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider?.unbindAll()
                cameraProvider?.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    preview,
                    imageCapture
                )
                continuation.resume(Unit)
            } catch (e: Exception) {
                Log.e("CameraManager", "Błąd bindowania kamery", e)
                continuation.resume(Unit)
            }
        }, ContextCompat.getMainExecutor(context))
    }

    /**
     * Robi zdjęcie i zwraca jako Bitmap - TYLKO obszar widoczny w ramce!
     * 
     * @param previewWidth - szerokość podglądu na ekranie (px)
     * @param previewHeight - wysokość podglądu na ekranie (px)
     * @param frameSize - rozmiar ramki na ekranie (px)
     */
    suspend fun takePhoto(
        previewWidth: Int,
        previewHeight: Int,
        frameSize: Int
    ): Bitmap? = suspendCoroutine { continuation ->
        val capture = imageCapture ?: run {
            continuation.resume(null)
            return@suspendCoroutine
        }

        capture.takePicture(
            cameraExecutor,
            object : ImageCapture.OnImageCapturedCallback() {
                override fun onCaptureSuccess(image: ImageProxy) {
                    Log.d("CameraManager", "Zdjęcie zrobione! Format: ${image.format}, Size: ${image.width}x${image.height}")
                    Log.d("CameraManager", "Preview: ${previewWidth}x${previewHeight}, Frame: $frameSize")
                    
                    val fullBitmap = imageProxyToBitmap(image)
                    image.close()
                    
                    Log.d("CameraManager", "Full bitmap: ${fullBitmap?.width}x${fullBitmap?.height}")
                    
                    // Wytnij DOKŁADNIE obszar ramki z obrazu
                    val croppedBitmap = fullBitmap?.let { 
                        cropFrameArea(it, previewWidth, previewHeight, frameSize) 
                    }
                    
                    Log.d("CameraManager", "Cropped bitmap: ${croppedBitmap?.width}x${croppedBitmap?.height}")
                    
                    // DEBUG: Zapisz oba zdjęcia
                    croppedBitmap?.let { saveBitmapForDebug(it, "cropped") }
                    fullBitmap?.let { saveBitmapForDebug(it, "full") }
                    
                    continuation.resume(croppedBitmap)
                }

                override fun onError(exception: ImageCaptureException) {
                    Log.e("CameraManager", "Błąd robienia zdjęcia", exception)
                    continuation.resume(null)
                }
            }
        )
    }
    
    /**
     * Wycina DOKŁADNIE obszar który odpowiada ramce na ekranie
     * 
     * PreviewView z FIT_CENTER pokazuje obraz proporcjonalnie z czarnymi paskami.
     * Musimy obliczyć gdzie na obrazie znajduje się ramka.
     */
    private fun cropFrameArea(
        bitmap: Bitmap,
        previewWidth: Int,
        previewHeight: Int,
        frameSize: Int
    ): Bitmap {
        val imgW = bitmap.width.toFloat()
        val imgH = bitmap.height.toFloat()
        
        // Oblicz jak PreviewView (FIT_CENTER) skaluje obraz
        // Proporcje podglądu i obrazu
        val previewAspect = previewWidth.toFloat() / previewHeight
        val imageAspect = imgW / imgH
        
        // Rozmiar obrazu wyświetlanego w preview (po FIT_CENTER)
        val displayedWidth: Float
        val displayedHeight: Float
        val offsetX: Float
        val offsetY: Float
        
        if (imageAspect > previewAspect) {
            // Obraz szerszy - paski na górze i dole
            displayedWidth = previewWidth.toFloat()
            displayedHeight = previewWidth / imageAspect
            offsetX = 0f
            offsetY = (previewHeight - displayedHeight) / 2
        } else {
            // Obraz wyższy - paski po bokach
            displayedHeight = previewHeight.toFloat()
            displayedWidth = previewHeight * imageAspect
            offsetX = (previewWidth - displayedWidth) / 2
            offsetY = 0f
        }
        
        // Skala: ile pikseli obrazu = 1 piksel na ekranie
        val scale = imgW / displayedWidth
        
        // Pozycja ramki na ekranie (środek)
        val frameCenterX = previewWidth / 2f
        val frameCenterY = previewHeight / 2f
        
        // Przelicz pozycję ramki na współrzędne obrazu
        // Ramka jest na środku ekranu, więc jej pozycja względem wyświetlanego obrazu:
        val frameInDisplayX = frameCenterX - offsetX
        val frameInDisplayY = frameCenterY - offsetY
        
        // Przelicz na piksele obrazu
        val cropCenterX = frameInDisplayX * scale
        val cropCenterY = frameInDisplayY * scale
        val cropSize = (frameSize * scale).toInt()
        
        // Oblicz prostokąt do wycięcia
        var cropX = (cropCenterX - cropSize / 2).toInt()
        var cropY = (cropCenterY - cropSize / 2).toInt()
        
        // Upewnij się że nie wychodzimy poza obraz
        cropX = cropX.coerceIn(0, (imgW - cropSize).toInt().coerceAtLeast(0))
        cropY = cropY.coerceIn(0, (imgH - cropSize).toInt().coerceAtLeast(0))
        val finalSize = cropSize.coerceAtMost(minOf(imgW.toInt() - cropX, imgH.toInt() - cropY))
        
        Log.d("CameraManager", "Crop: x=$cropX, y=$cropY, size=$finalSize (scale=$scale)")
        
        return Bitmap.createBitmap(bitmap, cropX, cropY, finalSize, finalSize)
    }
    
    /**
     * DEBUG: Zapisuje Bitmap do pliku w Downloads
     */
    private fun saveBitmapForDebug(bitmap: Bitmap, prefix: String = "debug") {
        try {
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val file = File(downloadsDir, "skin_scanner_${prefix}_${System.currentTimeMillis()}.jpg")
            FileOutputStream(file).use { out ->
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out)
            }
            Log.d("CameraManager", "DEBUG: Zdjęcie zapisane do: ${file.absolutePath}")
        } catch (e: Exception) {
            Log.e("CameraManager", "DEBUG: Błąd zapisu zdjęcia", e)
        }
    }

    /**
     * Konwertuje ImageProxy na Bitmap z poprawną rotacją
     * Obsługuje zarówno JPEG jak i YUV format
     */
    private fun imageProxyToBitmap(image: ImageProxy): Bitmap {
        val bitmap = when (image.format) {
            ImageFormat.JPEG -> {
                // Format JPEG - bezpośrednie dekodowanie
                val buffer = image.planes[0].buffer
                val bytes = ByteArray(buffer.remaining())
                buffer.get(bytes)
                BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            }
            ImageFormat.YUV_420_888 -> {
                // Format YUV - konwersja przez YuvImage
                yuvToRgb(image)
            }
            else -> {
                // Fallback - spróbuj jako JPEG
                val buffer = image.planes[0].buffer
                val bytes = ByteArray(buffer.remaining())
                buffer.get(bytes)
                BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            }
        }

        // Obróć obraz zgodnie z rotacją sensora
        val rotationDegrees = image.imageInfo.rotationDegrees
        return if (rotationDegrees != 0 && bitmap != null) {
            val matrix = Matrix().apply { postRotate(rotationDegrees.toFloat()) }
            Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
        } else {
            bitmap ?: throw IllegalStateException("Nie udało się przekonwertować obrazu")
        }
    }

    /**
     * Konwertuje YUV_420_888 na RGB Bitmap
     */
    private fun yuvToRgb(image: ImageProxy): Bitmap {
        val yBuffer = image.planes[0].buffer
        val uBuffer = image.planes[1].buffer
        val vBuffer = image.planes[2].buffer

        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()

        val nv21 = ByteArray(ySize + uSize + vSize)

        yBuffer.get(nv21, 0, ySize)
        vBuffer.get(nv21, ySize, vSize)
        uBuffer.get(nv21, ySize + vSize, uSize)

        val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(Rect(0, 0, image.width, image.height), 100, out)
        val imageBytes = out.toByteArray()
        return BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
    }

    /**
     * Zwalnia zasoby kamery
     */
    fun shutdown() {
        cameraProvider?.unbindAll()
        cameraExecutor.shutdown()
    }
}
