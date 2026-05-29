#!/usr/bin/env python
"""Health check per il servizio AI Router (NiceGUI + Ollama)."""
import sys

from config import Config
from ollama_service import check_ollama_health


def check_server_health(config: Config) -> bool:
    try:
        import requests
        host = "127.0.0.1" if config.SERVER_HOST == "0.0.0.0" else config.SERVER_HOST
        r = requests.get(f"http://{host}:{config.SERVER_PORT}", timeout=5)
        return r.status_code in (200, 405)
    except Exception:
        return False


if __name__ == "__main__":
    conf = Config()
    server_ok = check_server_health(conf)
    print(f"NiceGUI Server: {'OK' if server_ok else 'FAILED'}")
    print(f"Ollama: {'OK' if check_ollama_health(conf) else 'FAILED'}")
    sys.exit(0 if server_ok else 1)
