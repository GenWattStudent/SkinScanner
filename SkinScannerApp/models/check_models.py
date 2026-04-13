import torch
import sys
import os
from collections import defaultdict

def clean_name(name):
    # usuń prefix z DataParallel
    if name.startswith("module."):
        name = name[len("module."):]
    return name

def get_layer_id(name):
    """
    Wyciąga ID warstwy (bez weight/bias itd.)
    np:
    layer1.0.conv1.weight -> layer1.0.conv1
    fc.bias -> fc
    """
    parts = name.split(".")
    return ".".join(parts[:-1])  # usuwamy ostatni element (weight/bias)

def get_layer_type(name):
    name = name.lower()
    if "conv" in name:
        return "Conv"
    elif "bn" in name or "batchnorm" in name:
        return "BatchNorm"
    elif "fc" in name or "linear" in name:
        return "Linear"
    else:
        return "Other"

def sprawdz_model(sciezka_pth):
    print(f"\n{'='*60}")
    print(f"Plik: {os.path.basename(sciezka_pth)}")
    print(f"{'='*60}")

    try:
        state_dict = torch.load(sciezka_pth, map_location='cpu', weights_only=True)
    except Exception:
        state_dict = torch.load(sciezka_pth, map_location='cpu')

    if not isinstance(state_dict, dict):
        print("Nieobsługiwany format pliku.")
        return

    total_params = 0

    # unikalne warstwy
    unique_layers = {}
    layer_types = defaultdict(int)

    for name, tensor in state_dict.items():
        name = clean_name(name)

        param_count = tensor.numel()
        total_params += param_count

        layer_id = get_layer_id(name)

        # zapisujemy tylko raz na warstwę
        if layer_id not in unique_layers:
            layer_type = get_layer_type(layer_id)
            unique_layers[layer_id] = layer_type
            layer_types[layer_type] += 1

    # ===== OUTPUT =====
    print("\nPODSUMOWANIE WARSTW:")
    print(f"{'Typ':<15} {'Ilość':>10}")
    print("-" * 30)

    total_layers = 0
    for layer_type in sorted(layer_types.keys()):
        count = layer_types[layer_type]
        total_layers += count
        print(f"{layer_type:<15} {count:>10}")

    print("-" * 30)
    print(f"{'WSZYSTKIE':<15} {total_layers:>10}")

    print("\nPARAMETRY:")
    print(f"Łącznie: {total_params:,}")
    print(f"W milionach: {total_params / 1_000_000:.2f}M")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python sprawdz_model.py model.pth")
    else:
        for sciezka in sys.argv[1:]:
            if os.path.exists(sciezka):
                sprawdz_model(sciezka)
            else:
                print(f"Błąd: nie znaleziono pliku '{sciezka}'")