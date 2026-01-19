package com.example.skinscannerapp.data.repository

import android.content.Context
import com.example.skinscannerapp.domain.model.MLModel

/**
 * Repozytorium zarządzające dostępnymi modelami ML
 * SOLID: Single Responsibility - tylko zarządzanie modelami
 */
class ModelRepository(private val context: Context) {

    companion object {
        private const val MODELS_DIR = "models"
    }

    /**
     * Pobiera listę wszystkich dostępnych modeli z folderu assets/models
     */
    fun getAvailableModels(): List<MLModel> {
        return try {
            val modelFiles = context.assets.list(MODELS_DIR) ?: emptyArray()
            modelFiles
                .filter { it.endsWith(".ptl") || it.endsWith(".pt") }
                .map { fileName ->
                    MLModel(
                        id = fileName.substringBeforeLast("."),
                        displayName = getDisplayName(fileName),
                        fileName = "$MODELS_DIR/$fileName",
                        description = getModelDescription(fileName)
                    )
                }
        } catch (e: Exception) {
            emptyList()
        }
    }

    /**
     * Pobiera domyślny model (pierwszy dostępny)
     */
    fun getDefaultModel(): MLModel? {
        return getAvailableModels().firstOrNull()
    }

    /**
     * Pobiera model po ID
     */
    fun getModelById(id: String): MLModel? {
        return getAvailableModels().find { it.id == id }
    }

    private fun getDisplayName(fileName: String): String {
        return when {
            fileName.contains("MobileNetV3", ignoreCase = true) -> "MobileNetV3 (Szybki)"
            fileName.contains("ResNet", ignoreCase = true) -> "ResNet50 (Dokładny)"
            fileName.contains("ViT", ignoreCase = true) -> "Vision Transformer (Najdokładniejszy)"
            fileName.contains("CustomCNN", ignoreCase = true) -> "Custom CNN (Lekki)"
            else -> fileName.substringBeforeLast(".")
        }
    }

    private fun getModelDescription(fileName: String): String {
        return when {
            fileName.contains("MobileNetV3", ignoreCase = true) -> 
                "Zoptymalizowany dla urządzeń mobilnych. Najlepszy balans między szybkością a dokładnością."
            fileName.contains("ResNet", ignoreCase = true) -> 
                "Głęboka sieć rezydualna. Wysoka dokładność, wolniejsza predykcja."
            fileName.contains("ViT", ignoreCase = true) -> 
                "Vision Transformer. Najwyższa dokładność, wymaga więcej zasobów."
            fileName.contains("CustomCNN", ignoreCase = true) -> 
                "Prosta sieć konwolucyjna. Najszybsza, niższa dokładność."
            else -> "Model do klasyfikacji chorób skóry"
        }
    }
}
