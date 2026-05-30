#!/usr/bin/env python3
"""Test backend modules can be imported and initialized."""
import sys
import json
from pathlib import Path

print("=" * 70)
print("PHASE 1: Testing Python Environment & Core Modules")
print("=" * 70)

# Test 1: Python Version
print(f"\n✓ Python {sys.version.split()[0]}")
print(f"  Working Dir: {Path.cwd()}")

# Test 2: Config
print("\n--- Testing config.py ---")
try:
    from config import Config
    config = Config()
    print(f"✓ Config loaded")
    print(f"  Server: {config.SERVER_HOST}:{config.SERVER_PORT}")
    print(f"  Model: {config.EMBEDDING_MODEL}")
    print(f"  Training Data: {config.TRAINING_DATA_PATH}")
except Exception as e:
    print(f"✗ Config error: {e}")
    sys.exit(1)

# Test 3: Training Data
print("\n--- Testing training_data.json ---")
try:
    with open(config.TRAINING_DATA_PATH) as f:
        data = json.load(f)
    models = sorted(set(item['modello'] for item in data))
    print(f"✓ Training data: {len(data)} samples, {len(models)} models")
    print(f"  Sample: {models[0]}, {models[1]}, {models[2]}...")
except Exception as e:
    print(f"✗ Training data error: {e}")
    sys.exit(1)

# Test 4: Ollama Service (optional)
print("\n--- Testing ollama_service.py ---")
try:
    from ollama_service import check_ollama_health
    if check_ollama_health(config):
        print(f"✓ Ollama available at {config.OLLAMA_BASE_URL}")
    else:
        print(f"⚠ Ollama not running (optional)")
except ImportError as e:
    print(f"⚠ Module import issue: {e}")
except Exception as e:
    print(f"⚠ Ollama check error: {e}")

# Test 5: Predictor
print("\n--- Testing predictor.py ---")
try:
    # These require heavy ML libs
    from cache import ModelCache
    from predictor import predict_model
    print("✓ Predictor modules imported (ML libs present)")
except ImportError as e:
    print(f"⚠ ML dependencies missing: {e}")
    print("  Install: pip3 install sentence-transformers scikit-learn")

# Test 6: NiceGUI App
print("\n--- Testing nicegui_app.py ---")
try:
    import nicegui_app
    print("✓ NiceGUI app module imported")
    print(f"  Has run(): {hasattr(nicegui_app, 'run')}")
except ImportError as e:
    print(f"✗ nicegui missing: {e}")
    print("  Install: pip3 install nicegui")
    sys.exit(1)

print("\n" + "=" * 70)
print("PHASE 1 RESULT: Core modules ready")
print("=" * 70)
print("\nNext: Install Python dependencies if needed")
print("Then: Start backend with 'python3 router_main.py'")
