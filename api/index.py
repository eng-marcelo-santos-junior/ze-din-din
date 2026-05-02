import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Declarado no topo para que a análise estática do Vercel encontre 'app'
app = None  # noqa: F841 — será sobrescrito abaixo

try:
    from app import create_app
    app = create_app('production')
except Exception:
    import traceback
    from flask import Flask, Response
    _tb = traceback.format_exc()
    print(_tb, file=sys.stderr)
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def _startup_error(path):
        return Response(_tb, status=500, mimetype='text/plain')
