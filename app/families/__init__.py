from flask import Blueprint

families_bp = Blueprint('families', __name__)

from . import routes  # noqa
