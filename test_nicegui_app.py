
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
