import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Log all DB-related env var names (not values) to Vercel function logs for debugging
_db_vars = [k for k in os.environ if any(x in k.upper() for x in ('DATABASE', 'POSTGRES', 'NEON', 'PG'))]
print(f"[startup] DB env vars present: {_db_vars}", file=sys.stderr)

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
