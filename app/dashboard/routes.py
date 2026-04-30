from flask import render_template, g
from flask_login import login_required
from . import dashboard_bp
from ..utils.decorators import family_required


@dashboard_bp.route('/dashboard')
@login_required
@family_required
def index():
    return render_template('dashboard/index.html', family=g.current_family)
