package com.example.skinscannerapp.ui.screens

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.PhotoLibrary
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.skinscannerapp.data.classifier.PyTorchClassifier
import com.example.skinscannerapp.data.repository.ModelRepository
import com.example.skinscannerapp.domain.model.MLModel
import com.example.skinscannerapp.ui.components.ModelSelector
import com.example.skinscannerapp.ui.components.PredictionResults
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Główny ekran aplikacji - analiza zdjęć skóry
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onOpenCamera: () -> Unit,
    capturedPhoto: Bitmap?,
    onClearPhoto: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // Repozytoria i klasyfikator
    val modelRepository = remember { ModelRepository(context) }
    val classifier = remember { PyTorchClassifier(context) }

    // Stan
    var availableModels by remember { mutableStateOf<List<MLModel>>(emptyList()) }
    var selectedModel by remember { mutableStateOf<MLModel?>(null) }
    var selectedBitmap by remember { mutableStateOf<Bitmap?>(null) }
    var predictions by remember { mutableStateOf<List<Pair<String, Float>>>(emptyList()) }
    var isLoading by remember { mutableStateOf(false) }
    var isModelLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    // Użyj zdjęcia z kamery jeśli jest
    LaunchedEffect(capturedPhoto) {
        capturedPhoto?.let {
            selectedBitmap = it
            predictions = emptyList()
        }
    }

    // Załaduj dostępne modele
    LaunchedEffect(Unit) {
        availableModels = modelRepository.getAvailableModels()
        selectedModel = modelRepository.getDefaultModel()
    }

    // Załaduj model gdy się zmieni
    LaunchedEffect(selectedModel) {
        selectedModel?.let { model ->
            isModelLoading = true
            errorMessage = null
            try {
                withContext(Dispatchers.IO) {
                    classifier.loadModel(model.fileName)
                }
            } catch (e: Exception) {
                errorMessage = "Błąd ładowania modelu: ${e.message}"
            }
            isModelLoading = false
        }
    }

    // Launcher do wyboru zdjęcia z galerii
    val imagePickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            context.contentResolver.openInputStream(it)?.use { stream ->
                selectedBitmap = BitmapFactory.decodeStream(stream)
                predictions = emptyList()
                onClearPhoto()
            }
        }
    }

    // Funkcja analizy
    fun analyzeImage() {
        val bitmap = selectedBitmap ?: return
        if (!classifier.isModelLoaded()) {
            errorMessage = "Model nie jest załadowany"
            return
        }

        isLoading = true
        errorMessage = null

        scope.launch {
            try {
                val results = withContext(Dispatchers.Default) {
                    classifier.classify(bitmap)
                }
                predictions = results
            } catch (e: Exception) {
                errorMessage = "Błąd analizy: ${e.message}"
            }
            isLoading = false
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "Skin Scanner",
                        fontWeight = FontWeight.Bold
                    )
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // Selektor modelu
            if (availableModels.isNotEmpty()) {
                ModelSelector(
                    models = availableModels,
                    selectedModel = selectedModel,
                    onModelSelected = { model ->
                        selectedModel = model
                        predictions = emptyList()
                    },
                    modifier = Modifier.fillMaxWidth()
                )

                if (isModelLoading) {
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
                    Text(
                        text = "Ładowanie modelu...",
                        style = MaterialTheme.typography.bodySmall
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))
            }

            // Przyciski wyboru źródła zdjęcia
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Przycisk kamery
                OutlinedButton(
                    onClick = onOpenCamera,
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.CameraAlt,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Kamera")
                }

                // Przycisk galerii
                OutlinedButton(
                    onClick = { imagePickerLauncher.launch("image/*") },
                    modifier = Modifier.weight(1f)
                ) {
                    Icon(
                        imageVector = Icons.Default.PhotoLibrary,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Galeria")
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Podgląd wybranego zdjęcia
            selectedBitmap?.let { bitmap ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Image(
                        bitmap = bitmap.asImageBitmap(),
                        contentDescription = "Wybrane zdjęcie",
                        modifier = Modifier
                            .fillMaxSize()
                            .clip(RoundedCornerShape(16.dp)),
                        contentScale = ContentScale.Crop
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Przycisk analizy
                Button(
                    onClick = { analyzeImage() },
                    enabled = !isLoading && !isModelLoading && classifier.isModelLoaded(),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp)
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Analizowanie...")
                    } else {
                        Text(
                            text = "Analizuj zdjęcie",
                            style = MaterialTheme.typography.titleMedium
                        )
                    }
                }
            } ?: run {
                // Placeholder gdy nie ma zdjęcia
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                imageVector = Icons.Default.CameraAlt,
                                contentDescription = null,
                                modifier = Modifier.size(64.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = "Zrób zdjęcie lub wybierz z galerii",
                                style = MaterialTheme.typography.bodyLarge,
                                textAlign = TextAlign.Center,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }

            // Błąd
            errorMessage?.let { error ->
                Spacer(modifier = Modifier.height(8.dp))
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.padding(16.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer
                    )
                }
            }

            // Wyniki predykcji
            if (predictions.isNotEmpty()) {
                Spacer(modifier = Modifier.height(24.dp))
                PredictionResults(
                    predictions = predictions,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
