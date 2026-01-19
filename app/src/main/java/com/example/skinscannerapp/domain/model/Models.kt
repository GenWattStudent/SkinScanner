package com.example.skinscannerapp.domain.model

/**
 * Reprezentuje dostępny model ML do klasyfikacji
 */
data class MLModel(
    val id: String,
    val displayName: String,
    val fileName: String,
    val description: String
)

/**
 * Wynik pojedynczej predykcji
 */
data class PredictionResult(
    val className: String,
    val confidence: Float,
    val classIndex: Int
)

/**
 * Wynik analizy obrazu
 */
data class AnalysisResult(
    val predictions: List<PredictionResult>,
    val modelUsed: MLModel,
    val inferenceTimeMs: Long
)
