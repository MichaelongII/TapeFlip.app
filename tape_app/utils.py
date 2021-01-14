from flask import render_template
from flask_login import current_user

def render_page(template, current_user=current_user, **kwargs):
    """
        Renders a template, passing in some basic values to the template.
    """
    admin = False
    is_authenticated = current_user.is_authenticated

    if is_authenticated:
        if current_user.role == 'admin':
            admin = True

    return render_template(template, admin=admin, is_authenticated=is_authenticated, current_user=current_user, **kwargs)
