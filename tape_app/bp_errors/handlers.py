from flask import Blueprint, render_template

bp_errors = Blueprint('bp_errors', __name__)

@bp_errors.app_errorhandler(404)
def error_404(error):
    """
        Handels 404 error Page Not Found.
    """
    return render_template('errors/404.html'), 404

@bp_errors.app_errorhandler(403)
def error_403(error):
    """
        Handels 403 error Access Forbidden.
    """
    return render_template('errors/403.html'), 403

@bp_errors.app_errorhandler(500)
def error_500(error):
    """
        Handels 500 error Internal Error.
    """
    return render_template('errors/500.html'), 500
