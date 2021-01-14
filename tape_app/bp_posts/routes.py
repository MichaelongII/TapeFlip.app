from flask import Blueprint
from tape_app import db
from flask import redirect, url_for, abort
from tape_app.bp_posts.forms import SessionForm
from tape_app.models import Session, Sound
from tape_app.utils import render_page
from flask_login import current_user, login_required
from tape_app.bp_posts.utils import save_audio_file, get_sound_credits
from tape_app.bp_mail.email_utils import send_txt

bp_posts = Blueprint("bp_posts", __name__)

@bp_posts.route("/new_session",methods=['GET',"POST"])
@login_required
def new_session():
    """
        Creates a new session, is a dynamic form to add sounds files to session.
    """
    form = SessionForm()
    if form.validate_on_submit():
        # Create session
        new_session = Session()
        new_session.user_id = current_user.id
        new_session.session_name = form.session_name.data
        db.session.add(new_session)

        sound_num = 1  # sound_num is used to name audio files
        for sound in form.sounds.data:
            # Create sound
            new_sound = Sound()
            new_sound.options = sound['options']
            new_sound.machine = sound['machine']
            new_sound.file_name = save_audio_file(
                sound['file_name'],
                sound_num,
                new_session.id,
                current_user.id)
            new_session.sounds.append(new_sound)

            sound_num += 1

        db.session.commit()
        return redirect(url_for('bp_posts.session',session_id=new_session.id))

    return render_page("form.html",form=form, title='New Session', include_form_script=True)

@bp_posts.route("/session/<int:session_id>",methods=['GET',"POST"])
@login_required
def session(session_id):
    """
        Session view for user, gives a breakdown of credit costs of each of
        the sound files and a total. User's can remove sounds from session if they
        wish.

        session_id: int
    """
    # get the session by id
    session = Session.query.get_or_404(session_id)

    if current_user != session.user:
        abort(403)  # only the user that's session it should be able to view

    session_credits = 0
    # only have to assign credits once
    if session.sounds[0].credits == 0:
        for sound in session.sounds:
            # assign credit amount to each sound
            credits = get_sound_credits(sound, current_user.id)
            sound.credits = credits
            session_credits += credits

        # assing total credit amount for session
        session.credits = session_credits
        db.session.commit()

    return render_page("user/session.html", session=session, total_credits=session.credits, title='Session')

@bp_posts.route("/submit_session/<int:session_id>",methods=['GET',"POST"])
@login_required
def submit_session(session_id):
    """
        Submits a session for recording.

        session_id: int
    """
    # get the session by id
    session = Session.query.get_or_404(session_id)

    if current_user != session.user:
        abort(403)  # only the user that's session it should be able to submit

    session.submitted = True
    current_user.credits -= session.credits
    db.session.commit()

    return redirect(url_for('bp_posts.session', session_id=session_id))

@bp_posts.route("/remove_file/<int:sound_id>",methods=['GET',"POST"])
@login_required
def remove_file(sound_id):
    """
        Removes a sound from a session, and if that is the only sound
        in the session, deletes the session.

        sound_id: int
    """
    # get sound by id
    sound = Sound.query.get_or_404(sound_id)
    # get session by sound id
    session = Session.query.get_or_404(sound.session_id)

    if current_user != session.user:
        abort(403)  # only the user that's session it should be able to delete sound

    # delete sound and update session's credits
    session.sounds.remove(sound)
    session.credits -= sound.credits
    db.session.delete(sound)
    db.session.commit()

    # delete session if last sound was deleted
    if Sound.query.filter_by(session_id=session.id).count() == 0:
        db.session.delete(session)
        db.session.commit()
        return redirect(url_for('bp_users.profile'))

    return redirect(url_for('bp_posts.session',session_id=session.id))


@bp_posts.route("/download_zip/<int:session_id>", methods=['GET', 'POST'])
@login_required
def download_zip(session_id):
    """
        Downloads user's zip file of finished files
    """
    session = Session.query.filter_by(id=session_id).first()

    return redirect(url_for('bp_admin.usr', user_id=session.user.id, filename=session.zip_file_name))
