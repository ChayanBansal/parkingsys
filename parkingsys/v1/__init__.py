from flask import Blueprint, request
from parkingsys.db import close_db, close_doc_db, get_db, get_doc_db

api_bp = Blueprint("v1", __name__, url_prefix="/api/v1/")

@api_bp.before_app_request
def load_required_info():
    get_db()
    get_doc_db()

@api_bp.after_app_request
def clear_resources(response):
    close_db()
    close_doc_db()
    return response

from parkingsys.v1 import routes