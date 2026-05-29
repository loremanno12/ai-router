"""NiceGUI orchestrator che serve la UI buildata in `frontend` e fa da bridge
tra l'iframe (frontend) e i moduli Python (`predictor`, `ollama_service`).

Design:
- monta i file statici in `/frontend` (serve `index.html` generato da Vite)
- rende un iframe full-screen che carica `/frontend/index.html`
- usa una `ui.timer` che polla `window.__ai_router_request__` nel client
  (via `ui.run_javascript`) per ricevere richieste dall'iframe
- elabora le azioni `optimize` e `route` invocando le funzioni Python
- risponde impostando `window.__ai_router_response__` e dispatchando
  `ai:response` in pagina, così l'iframe può riceverla con
  `window.parent.addEventListener('ai:response', ...)`.

Nota: mantiene i moduli Python modulari — questo file è solo l'orchestratore UI.
"""
import json
import logging
import os
from typing import Any

from nicegui import ui, app

from config import Config

# Lazy-loaded heavy components (initialized in `run()` to avoid importing
# heavy ML libs at module import time which breaks reload/multiprocess on Windows)
ModelCache = None
predict_model = None
improve_prompt_with_ollama = None
check_ollama_health = None
MetricsCollector = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _static_dir_path() -> str:
    root = os.path.dirname(__file__)
    # prefer frontend/dist if exists (after build/copy)
    candidate = os.path.join(root, 'frontend')
    if os.path.isdir(os.path.join(candidate, 'dist')):
        return os.path.join(candidate, 'dist')
    return candidate


config = None
model_cache = None
metrics_collector = None


# Note: mounting of static files is performed inside `_setup_ui()` to avoid
# modifying the Starlette/FastAPI app at import time (which can conflict
# with NiceGUI's script-mode checks).
static_root = _static_dir_path()


def _setup_ui() -> None:
    # Define page(s) and register timers inside this function so that
    # importing this module does not create UI elements in the global scope.
    # Mount static files (Vite build output should be copied to frontend/ or frontend/dist)
    if os.path.isdir(static_root):
        try:
            from starlette.staticfiles import StaticFiles

            app.mount('/frontend', StaticFiles(directory=static_root), name='frontend')
            logger.info('Static files mounted at /frontend -> %s', static_root)

            # Also mount common absolute asset paths so builds that reference
            # `/assets/...` or `/manifest.json` still work when the SPA is
            # served under `/frontend` (some Vite builds use absolute paths).
            try:
                assets_dir = os.path.join(static_root, 'assets')
                if os.path.isdir(assets_dir):
                    app.mount('/assets', StaticFiles(directory=assets_dir), name='assets')
                    logger.info('Mounted assets at /assets -> %s', assets_dir)
                # serve manifest.json at root if present
                manifest_path = os.path.join(static_root, 'manifest.json')
                if os.path.isfile(manifest_path):
                    from starlette.responses import FileResponse

                    def _manifest(request):
                        return FileResponse(manifest_path)

                    app.add_api_route('/manifest.json', _manifest, methods=['GET'])
                    logger.info('Registered /manifest.json -> %s', manifest_path)
            except Exception:
                logger.exception('Errore montando asset/manifest statici')

            try:
                from starlette.responses import RedirectResponse

                def _root_redirect():
                    return RedirectResponse(url='/frontend/index.html')

                app.add_api_route('/', _root_redirect, methods=['GET'])
                logger.info('Registered root redirect to /frontend/index.html')
            except Exception:
                logger.exception('Unable to register root redirect to frontend index')
        except Exception:
            logger.exception('Errore montando static files')
    else:
        logger.warning('Nessuna cartella frontend trovata in %s — assicurati di aver eseguito il build', static_root)
        # Register a plain FastAPI route (via NiceGUI's underlying `app`) to
        # serve the fullscreen iframe. Avoid using `ui.page` here because
        # some NiceGUI runtime modes disallow `ui.page` when UI is defined
        # in the global scope (script mode).
        try:
                from starlette.responses import HTMLResponse

                def index(request):
                        iframe_src = '/frontend/index.html'
                        html = f"""
                        <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
                        <body style="height:100vh;margin:0">
                        <iframe id="ai-iframe" src="{iframe_src}" style="border:none;width:100vw;height:100vh;" sandbox="allow-scripts allow-same-origin allow-forms"></iframe>
                        <script>
                            // bridge globals used by the iframe
                            window.__ai_router_request__ = null;
                            window.__ai_router_response__ = null;
                        </script>
                        </body></html>
                        """
                        return HTMLResponse(html)

                app.add_api_route('/', index, methods=['GET'])
                logger.info('Registered root HTML route at /')
        except Exception:
                logger.exception('Unable to register root route for iframe')

    # Register the poller as a repeating timer. Different NiceGUI versions
    # expose `ui.timer` with slightly different signatures: some accept
    # the callback as the second positional argument, others require
    # `callback=`. Try common variants for compatibility.
    try:
        ui.timer(0.5, _poll_requests)
    except TypeError:
        try:
            ui.timer(0.5, callback=_poll_requests)
        except Exception:
            logger.exception('Unable to register ui.timer for _poll_requests')


# Poller: legge richieste dall'iframe impostate su window.__ai_router_request__
# e risponde impostando window.__ai_router_response__ + dispatchEvent('ai:response').
async def _poll_requests() -> None:
    try:
        req = await ui.run_javascript('return window.__ai_router_request__ || null')
    except Exception:
        # client non connesso o errore JS
        return

    if not req:
        return

    # consume request
    await ui.run_javascript('window.__ai_router_request__ = null')

    try:
        req_id = req.get('id')
        action = req.get('action')
        payload: dict[str, Any] = req.get('payload') or {}
    except Exception as e:
        logger.exception('Request malformed: %s', e)
        return

    logger.info('Ricevuta richiesta dal frontend: %s', action)

    response_payload: dict[str, Any] = {'success': False, 'error': 'unknown'}

    try:
        if action == 'optimize':
            prompt = payload.get('prompt', '')
            result = improve_prompt_with_ollama(prompt, config, target_model=None)
            response_payload = {
                'optimized_prompt': result.get('improved_prompt'),
                'success': result.get('success', False),
                'error': result.get('error'),
                'elapsed_time': result.get('elapsed_time'),
            }
        elif action == 'route':
            prompt = payload.get('prompt', '')
            result = predict_model(prompt, config, model_cache)
            response_payload = {
                'recommended_model': result.get('predicted_model'),
                'confidence': result.get('confidence'),
                'all_probabilities': result.get('all_probabilities'),
                'success': result.get('success', False),
                'error': result.get('error'),
            }
        else:
            response_payload = {'success': False, 'error': f'unknown action {action}'}

    except Exception as e:
        logger.exception('Errore elaborando richiesta %s', action)
        response_payload = {'success': False, 'error': str(e)}

    response = {'id': req_id, 'payload': response_payload}

    # push response to page and dispatch event so iframe can pick it up
    try:
        js = f"window.__ai_router_response__ = {json.dumps(response)}; window.dispatchEvent(new CustomEvent('ai:response'));"
        await ui.run_javascript(js)
        logger.info('Risposta inviata al frontend (id=%s)', req_id)
    except Exception:
        logger.exception('Impossibile inviare risposta al frontend')


# Note: timer registration is performed inside `_setup_ui()` to avoid
# creating UI elements at import time. Do not register timers here.


def run(port: int = 7860) -> None:
    """Helper per avviare l'app NiceGUI sulla porta richiesta."""
    logger.info('Avvio NiceGUI orchestrator sulla porta %s', port)
    # Initialize heavy modules here (deferred to avoid import-time cost)
    global config, model_cache, metrics_collector
    global predict_model, improve_prompt_with_ollama, check_ollama_health

    try:
        config = Config()
    except Exception:
        logger.exception('Unable to load Config()')
        config = None

    try:
        from metrics import MetricsCollector as _MetricsCollector

        metrics_collector = _MetricsCollector()
    except Exception:
        metrics_collector = None
        logger.debug('MetricsCollector not available', exc_info=True)

    try:
        from cache import ModelCache as _ModelCache

        model_cache = _ModelCache()
    except Exception:
        model_cache = None
        logger.exception('Unable to initialize ModelCache')

    try:
        import predictor as _predictor_mod

        predict_model = getattr(_predictor_mod, 'predict_model', None)
        if metrics_collector and hasattr(_predictor_mod, 'metrics_collector'):
            _predictor_mod.metrics_collector = metrics_collector
    except Exception:
        predict_model = None
        logger.exception('Unable to import predictor')

    try:
        import ollama_service as _ollama_mod

        improve_prompt_with_ollama = getattr(_ollama_mod, 'improve_prompt_with_ollama', None)
        check_ollama_health = getattr(_ollama_mod, 'check_ollama_health', None)
    except Exception:
        improve_prompt_with_ollama = None
        check_ollama_health = None
        logger.debug('ollama_service not available', exc_info=True)

    # Setup UI pages/timers now (avoid creating UI at import time)
    _setup_ui()

    # Disable automatic reload to avoid multiple spawn/reload cycles on Windows
    # during development; explicit restarts are safer when working with heavy
    # ML imports.
    try:
        ui.run(port=port, reload=False)
    except TypeError:
        # Older NiceGUI versions may not accept reload parameter
        ui.run(port=port)


if __name__ == '__main__':
    run(7860)
