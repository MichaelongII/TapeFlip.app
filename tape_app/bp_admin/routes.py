from flask import Blueprint, request, send_from_directory, abort, redirect, url_for
from flask import current_app as app
from flask_login import login_required, current_user
import os
from tape_app import db
from tape_app.models import Session, User, Sound, FreeCreditCode
from tape_app.utils import render_page
from tape_app.bp_admin.utils import admin_required, id_generator
from tape_app.bp_users.forms import AddCreditsForm, CompleteSessionForm, FreeCreditCodeForm
from tape_app.bp_posts.utils import save_audio_file
from tape_app.bp_mail.email_utils import send_email
from tape_app.bp_mail.messages import complete_session_msg

bp_admin = Blueprint("bp_admin", __name__)

@bp_admin.route('/USR/<int:user_id>/<string:filename>')
@login_required
def usr(user_id, filename):
    """
        Serves a file from a User's directory.

        user_id: int
        filename: str
    """
    # if the current user is not an admin or the user that's directory
    # is being served from, abort
    if (current_user.role != "admin") or (current_user.id != user_id):
        abort(403)

    # get name of directory
    dir = "USR_" + str(user_id)

    return send_from_directory(os.path.join(app.root_path, 'protected', dir), filename, as_attachment=True)

@bp_admin.route('/admin_session_view/<int:session_id>', methods=["GET","POST"])
@login_required
@admin_required()
def admin_session_view(session_id):
    """
        Session view for admin to download, upload, and complete sessions.

        session_id: int
    """
    form = CompleteSessionForm()
    # get the session by id
    session = Session.query.get_or_404(session_id)

    if form.validate_on_submit():
        # file, sound_num, session_id, user_id, zip=False):
        zip_fn = save_audio_file(form.zip_file.data, 0, session.id, session.user.id)
        session.zip_file_name = zip_fn
        session.completed = True
        db.session.commit()

        send_email(subject="Your Files are ready to Download!",
                    msg_body=complete_session_msg(session),
                    button=("Go to Session", url_for('bp_posts.session', session_id=session.id)),
                    recipient=session.user,
                    send_txt=True,
                    emoji="✅ ")

        return redirect(url_for('bp_admin.admin_session_view', session_id=session.id))

    return render_page("admin/session.html", session=session, form=form, total_credits=session.credits, title='Session')

@bp_admin.route('/dashboard')
@login_required
@admin_required()
def dashboard():
    """
        Admin dashboard.
    """
    sessions_to_complete = Session.query.filter_by(submitted=True, completed=False)
    page = request.args.get('page', 1, type=int)

    sessions_paginated = sessions_to_complete\
        .order_by(Session.date_posted.desc())\
        .paginate(page=page, per_page=6)

    return render_page("admin/dashboard.html",sessions=sessions_paginated, title='Dashboard')

@bp_admin.route('/give_credits', methods=['GET', 'POST'])
@login_required
@admin_required()
def give_credits():
    """
        Form to give credits to a user.
    """
    form = AddCreditsForm()
    if form.validate_on_submit():

        # get user by username
        user = User.query.filter_by(username=form.username.data.lower()).first()
        user.credits += int(form.num_of_credits.data)
        db.session.commit()

        return redirect(url_for('bp_admin.dashboard'))

    return render_page("admin/add_credits.html", form=form, title='Give Credits')

@bp_admin.route('/create_code', methods=['GET', 'POST'])
@login_required
@admin_required()
def create_code():
    """
        Form to create some FreeCreditCodes
    """
    form = FreeCreditCodeForm()
    if form.validate_on_submit():

        for i in range(int(form.num_of_codes.data)):
            code_obj = FreeCreditCode(code=id_generator(prefix=form.prefix.data), credits=int(form.num_of_credits.data))
            db.session.add(code_obj)
            db.session.commit()

        return redirect(url_for('bp_admin.active_codes'))

    return render_page("admin/create_code.html", form=form, title='Give Credits')

@bp_admin.route('/delete_code/<int:code_id>', methods=['GET', 'POST'])
@login_required
@admin_required()
def delete_code(code_id):
    """
        Deletes a FreeCreditCode.

        code_id: int
    """
    code = FreeCreditCode.query.get_or_404(code_id)
    db.session.delete(code)
    db.session.commit()

    return redirect(url_for('bp_admin.active_codes'))

@bp_admin.route('/active_codes', methods=['GET', 'POST'])
@login_required
@admin_required()
def active_codes():
    """
        View all active FreeCreditCodes
    """
    codes = FreeCreditCode.query.all()

    return render_page("admin/active_codes.html", codes=codes, title='Codes')

@bp_admin.route('/download_sound/<int:sound_id>', methods=['GET', 'POST'])
@login_required
@admin_required()
def download_sound(sound_id):
    """
        Download sound for admin.

        sound_id: int
    """
    sound = Sound.query.filter_by(id=sound_id).first()
    session = Session.query.filter_by(id=sound.session.id).first()
    user = User.query.filter_by(id=session.user.id).first()

    return redirect(url_for('bp_admin.usr', user_id=user.id, filename=sound.file_name))
