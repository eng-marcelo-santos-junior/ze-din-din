from flask import Blueprint

budgets_bp = Blueprint('budgets', __name__)

from . import routes  # noqa
