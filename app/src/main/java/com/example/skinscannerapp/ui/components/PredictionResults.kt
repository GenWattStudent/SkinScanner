package com.example.skinscannerapp.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

/**
 * Komponent wyświetlający wyniki predykcji
 * DRY: Reużywalny komponent
 */
@Composable
fun PredictionResults(
    predictions: List<Pair<String, Float>>,
    modifier: Modifier = Modifier,
    maxResults: Int = 5
) {
    Column(modifier = modifier) {
        Text(
            text = "Wyniki analizy",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Używamy zwykłej Column zamiast LazyColumn (bo jesteśmy w scrollable parent)
        Column(
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            predictions.take(maxResults).forEachIndexed { index, (className, probability) ->
                PredictionCard(
                    rank = index + 1,
                    className = className,
                    probability = probability,
                    isTopResult = index == 0
                )
            }
        }
    }
}

@Composable
private fun PredictionCard(
    rank: Int,
    className: String,
    probability: Float,
    isTopResult: Boolean
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = if (isTopResult && probability > 50)
                MaterialTheme.colorScheme.primaryContainer
            else
                MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Numer rankingu
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = if (isTopResult)
                        MaterialTheme.colorScheme.primary
                    else
                        MaterialTheme.colorScheme.outline
                ) {
                    Text(
                        text = "#$rank",
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        style = MaterialTheme.typography.labelMedium,
                        color = if (isTopResult)
                            MaterialTheme.colorScheme.onPrimary
                        else
                            MaterialTheme.colorScheme.surface
                    )
                }

                Text(
                    text = className,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = if (isTopResult) FontWeight.Bold else FontWeight.Normal
                )
            }

            // Pasek procentowy
            Column(
                horizontalAlignment = Alignment.End
            ) {
                Text(
                    text = String.format("%.1f%%", probability),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = getConfidenceColor(probability)
                )
                
                LinearProgressIndicator(
                    progress = { probability / 100f },
                    modifier = Modifier
                        .width(80.dp)
                        .height(4.dp),
                    color = getConfidenceColor(probability),
                )
            }
        }
    }
}

@Composable
private fun getConfidenceColor(probability: Float) = when {
    probability >= 80 -> MaterialTheme.colorScheme.primary
    probability >= 50 -> MaterialTheme.colorScheme.tertiary
    probability >= 20 -> MaterialTheme.colorScheme.secondary
    else -> MaterialTheme.colorScheme.outline
}
