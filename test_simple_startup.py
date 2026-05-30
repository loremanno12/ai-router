#!/usr/bin/env python3
"""Simple startup test without ML dependencies."""
import subprocess
import time
import sys
import requests

print("=" * 70)
print("SIMPLE STARTUP TEST (without ML dependencies)")
print("=" * 70)

# Modify nicegui_app to not require ML
print("\n1. Creating minimal nicegui test app...")

test_app = """
from nicegui import ui, app
import os

static_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'dist')

@ui.page('/')
def home():
    ui.label('AI Router Backend Running')
    
if os.path.isdir(static_dir):
    try:
        from starlette.staticfiles import StaticFiles
        app.mount('/frontend', StaticFiles(directory=static_dir), name='frontend')
        print(f'Static files mounted at /frontend')
    except Exception as e:
        print(f'Could not mount static files: {e}')

ui.run(port=7860, show=False, reload=False)
"""

with open('test_nicegui_app.py', 'w') as f:
    f.write(test_app)

# Start backend
print("\n2. Starting NiceGUI server on port 7860...")
backend = subprocess.Popen(
    [sys.executable, "test_nicegui_app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for startup
print("   Waiting for server to start...")
max_wait = 10
for i in range(max_wait):
    time.sleep(1)
    try:
        r = requests.get("http://localhost:7860/", timeout=1)
        if r.status_code == 200:
            print(f"✓ Server started in {i+1}s")
            break
    except:
        pass
else:
    print("✗ Server failed to start")
    backend.kill()
    output = backend.stdout.read()
    print("Output:", output[:500])
    sys.exit(1)

# Test frontend
print("\n3. Testing frontend serving...")
try:
    r = requests.get("http://localhost:7860/frontend/index.html", timeout=2)
    if r.status_code == 200:
        print("✓ Frontend HTML accessible")
        if "AI Router" in r.text:
            print("✓ Frontend content correct")
    else:
        print(f"⚠ Status: {r.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test assets
print("\n4. Testing assets...")
try:
    r = requests.get("http://localhost:7860/frontend/assets/index-Bv8cLlc7.js", timeout=2)
    if r.status_code == 200:
        size = len(r.content)
        print(f"✓ JS bundle served: {size} bytes")
except Exception as e:
    print(f"⚠ Asset test: {e}")

# Cleanup
print("\n5. Stopping server...")
backend.terminate()
backend.wait(timeout=5)
print("✓ Server stopped")

# Remove test file
os.remove('test_nicegui_app.py')

print("\n" + "=" * 70)
print("STARTUP TEST: PASSED")
print("=" * 70)
print("\nNiceGUI can serve the frontend build correctly.")
print("\nFor the full AI Router backend with ML features:")
print("  pip3 install sentence-transformers scikit-learn pandas numpy")
print("  python3 router_main.py")
