package com.example.skinscannerapp.data.classifier

import android.content.Context
import android.graphics.Bitmap
import com.example.skinscannerapp.domain.classifier.ImageClassifier
import org.pytorch.IValue
import org.pytorch.LiteModuleLoader
import org.pytorch.Module
import org.pytorch.torchvision.TensorImageUtils
import java.io.File
import java.io.FileOutputStream

/**
 * Implementacja klasyfikatora używająca PyTorch Mobile
 * SOLID: Single Responsibility - tylko klasyfikacja obrazów
 */
class PyTorchClassifier(private val context: Context) : ImageClassifier {

    private var model: Module? = null
    private var currentModelPath: String? = null

    companion object {
        // 14 klas chorób skóry (kolejność MUSI być taka sama jak w treningu!)
        val CLASS_NAMES = arrayOf(
            "Actinic keratoses",           // 0 - Rogowacenie słoneczne
            "Basal cell carcinoma",        // 1 - Rak podstawnokomórkowy
            "Benign keratosis-like lesions", // 2 - Łagodne zmiany rogowaciejące
            "Chickenpox",                  // 3 - Ospa wietrzna
            "Cowpox",                      // 4 - Ospa krowia
            "Dermatofibroma",              // 5 - Włókniak skórny
            "HFMD",                        // 6 - Choroba rąk, stóp i ust
            "Healthy",                     // 7 - Zdrowa skóra
            "Measles",                     // 8 - Odra
            "Melanocytic nevi",            // 9 - Znamiona melanocytowe
            "Melanoma",                    // 10 - Czerniak
            "Monkeypox",                   // 11 - Małpia ospa
            "Squamous cell carcinoma",     // 12 - Rak płaskonabłonkowy
            "Vascular lesions"             // 13 - Zmiany naczyniowe
        )

        // Normalizacja ImageNet (taka sama jak w treningu!)
        private val MEAN = floatArrayOf(0.485f, 0.456f, 0.406f)
        private val STD = floatArrayOf(0.229f, 0.224f, 0.225f)
        private const val IMG_SIZE = 224
    }

    override fun loadModel(modelPath: String) {
        if (currentModelPath == modelPath && model != null) return

        // Zamknij poprzedni model
        model?.destroy()

        // Kopiuj model z assets do cache
        val modelFile = File(context.cacheDir, modelPath.substringAfterLast("/"))
        if (!modelFile.exists()) {
            context.assets.open(modelPath).use { input ->
                FileOutputStream(modelFile).use { output ->
                    input.copyTo(output)
                }
            }
        }

        model = LiteModuleLoader.load(modelFile.absolutePath)
        currentModelPath = modelPath
    }

    override fun classify(bitmap: Bitmap): List<Pair<String, Float>> {
        val module = model ?: throw IllegalStateException("Model nie załadowany!")

        // 1. Wytnij środkowy kwadrat z obrazu (usuwamy tło!)
        val croppedBitmap = cropCenterSquare(bitmap)
        
        // 2. Przeskaluj do 224x224
        val scaledBitmap = Bitmap.createScaledBitmap(croppedBitmap, IMG_SIZE, IMG_SIZE, true)

        // 3. Konwertuj Bitmap na tensor używając OFICJALNEJ biblioteki PyTorch!
        val inputTensor = TensorImageUtils.bitmapToFloat32Tensor(
            scaledBitmap,
            MEAN,  // ImageNet mean
            STD    // ImageNet std
        )

        // 3. Uruchom model
        val outputTensor = module.forward(IValue.from(inputTensor)).toTensor()
        val scores = outputTensor.dataAsFloatArray

        // 4. Softmax
        val probabilities = softmax(scores)

        // 5. Zwróć wyniki posortowane
        return CLASS_NAMES.indices
            .map { CLASS_NAMES[it] to probabilities[it] * 100f }
            .sortedByDescending { it.second }
    }

    override fun isModelLoaded(): Boolean = model != null

    override fun close() {
        model?.destroy()
        model = null
        currentModelPath = null
    }

    /**
     * Wycina środkowy kwadrat z obrazu - usuwa tło!
     * Dzięki temu model widzi tylko obszar zainteresowania
     */
    private fun cropCenterSquare(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        
        // Znajdź mniejszy wymiar
        val size = minOf(width, height)
        
        // Oblicz offset żeby wyciąć środek
        val x = (width - size) / 2
        val y = (height - size) / 2
        
        return Bitmap.createBitmap(bitmap, x, y, size, size)
    }

    private fun softmax(scores: FloatArray): FloatArray {
        val maxScore = scores.maxOrNull() ?: 0f
        val expScores = scores.map { kotlin.math.exp((it - maxScore).toDouble()).toFloat() }
        val sumExp = expScores.sum()
        return expScores.map { it / sumExp }.toFloatArray()
    }
}
