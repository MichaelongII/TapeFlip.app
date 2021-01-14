from flask import url_for, flash, redirect
from flask_login import current_user
from functools import wraps
import string
import random
from tape_app.models import FreeCreditCode

def admin_required(*roles):
    """
        Routes with this static method makes a route only
        accessable to admin.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role != "admin":
                flash("Sorry, you're not authroized to view that page.", 'danger')
                return redirect(url_for('main.home'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def id_generator(prefix="", size=6, chars=string.ascii_uppercase + string.digits):
    """
        Create a unique FreeCreditCode code
    """
    while True:
        code = prefix + ''.join(random.choice(chars) for _ in range(size))
        if FreeCreditCode.query.filter_by(code=code).count() == 0:
            return code
