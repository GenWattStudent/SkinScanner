package com.example.skinscannerapp.domain.classifier

import android.graphics.Bitmap

/**
 * Interfejs klasyfikatora obrazów - SOLID: Interface Segregation
 */
interface ImageClassifier {
    fun loadModel(modelPath: String)
    fun classify(bitmap: Bitmap): List<Pair<String, Float>>
    fun isModelLoaded(): Boolean
    fun close()
}
