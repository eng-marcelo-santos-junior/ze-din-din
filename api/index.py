import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = None

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
