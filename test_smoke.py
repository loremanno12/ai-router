"""Smoke test per il progetto ai-router.

Avvia `router_main.py` in un processo figlio (opzionale), attende che
`/frontend/index.html` sia raggiungibile su http://127.0.0.1:7860 e stampa
il risultato. Termina il server figlio alla fine del test.

Uso:
  python test_smoke.py        # avvia il server e testa
  python test_smoke.py --no-start  # non avvia il server, solo verifica
  python test_smoke.py --timeout 60

Il test usa solo librerie standard (urllib).
"""

from __future__ import annotations
import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
import signal
import os

ROOT = Path(__file__).resolve().parent
ROUTER_SCRIPT = ROOT / 'router_main.py'
DEFAULT_PORT = 7860

def build_urls(port: int) -> list[str]:
    return [f'http://127.0.0.1:{port}/frontend/index.html', f'http://127.0.0.1:{port}/']


def wait_for_url(url: str, timeout: int = 60, interval: float = 0.5):
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                body = resp.read()
                code = resp.getcode()
                return code, body
        except Exception as e:
            last_err = e
            time.sleep(interval)
    raise TimeoutError(f"Timeout waiting for {url}. Last error: {last_err}")


def start_server(log_path: Path):
    if not ROUTER_SCRIPT.exists():
        raise FileNotFoundError(f"Entry script not found: {ROUTER_SCRIPT}")
    # open log file for server stdout/stderr
    lf = open(log_path, 'w', encoding='utf-8', errors='replace')
    popen = subprocess.Popen(
        [sys.executable, str(ROUTER_SCRIPT)],
        cwd=str(ROUTER_SCRIPT.parent),
        stdout=lf,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
    )
    return popen, lf


def kill_proc_tree(p):
    try:
        p.terminate()
        p.wait(timeout=5)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser(description='Smoke test ai-router')
    parser.add_argument('--no-start', action='store_true', help='Non avviare il server (assumi già in esecuzione)')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Porta su cui verificare il server (default: 7860)')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout in secondi per lanciarsi e rispondere')
    parser.add_argument('--log', type=str, default='test_smoke_server.log', help='File di log per l\'output del server')
    args = parser.parse_args()

    server_proc = None
    log_file = None

    def _on_sig(signum, frame):
        print('\nInterrotto, terminando server figlio...')
        if server_proc:
            kill_proc_tree(server_proc)
        sys.exit(130)

    signal.signal(signal.SIGINT, _on_sig)
    signal.signal(signal.SIGTERM, _on_sig)

    try:
        if not args.no_start:
            print('Avvio server via', ROUTER_SCRIPT)
            server_proc, log_file = start_server(Path(args.log))
            print('Server avviato (pid=', server_proc.pid, '), attendo up to', args.timeout, 's...')
        else:
            print(f'Non avvio il server; verifico che sia già in ascolto su porta {args.port}')

        # attempt each URL in sequence until one succeeds
        success = False
        last_exc = None
        for url in build_urls(args.port):
            try:
                code, body = wait_for_url(url, timeout=args.timeout)
                print(f'OK: {url} -> HTTP {code}')
                txt = body.decode('utf-8', errors='replace')
                # quick sanity checks
                if '<iframe' in txt or '<div' in txt or 'window.__ai_router_request__' in txt or '<script' in txt:
                    print('Contenuto index verificato (sembra valido).')
                else:
                    print('Attenzione: contenuto recuperato ma non contiene marker attesi.')
                success = True
                break
            except Exception as e:
                last_exc = e
                # try next url
        if not success:
            print('ERRORE: nessuna URL ha risposto correttamente.', last_exc)
            raise RuntimeError('Smoke test fallito')

        print('Smoke test superato.')

    finally:
        if server_proc:
            print('Terminazione server figlio...')
            kill_proc_tree(server_proc)
            # close log file
            try:
                log_file.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()
