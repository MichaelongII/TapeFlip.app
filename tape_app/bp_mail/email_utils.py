from flask_mail import Message
from twilio.rest import Client
from flask import render_template, url_for
from tape_app import mail
from flask import current_app as app
from tape_app.bp_mail.utils import str_to_list

def send_txt(msg, to):
    """
        Sends a text to phone number "to" using twilio SDK.

        msg: str
        to: str: Phone number
    """
    num = "+" + to
    account_sid = app.config['TWILIO_SID']
    auth_token = app.config['TWILIO_AUTH']
    client = Client(account_sid, auth_token)
    try:
        message = client.messages \
            .create(
                body=msg,
                from_=app.config['TWILIO_PHONE_NUMBER'],
                to=num
            )
    except Exception as e:
        print("**TEXT_ERROR**")
        print(e)

def send_email(subject, msg_body, button, recipient, emoji="", send_txt=False):
    """
        Sends an email to user "recipient" and text if user has text_notif on.

        subject: str
        msg_body: str
        buttons: tuple: ("Click Me!", "url")
        recipient: User
        emoji: str
    """
    msg = Message(emoji + "Tape Flip -- " + subject, sender="reelone@tapeflip.app", recipients=[recipient.email])
    msg_list = str_to_list(msg_body)

    if recipient.text_notif and send_txt:
        if emoji != "":
            txt = emoji + msg_body
        else:
            txt = msg_body
        txt = txt + "\n\n" + button[1]
        send_txt(txt, recipient.phone_number)

    html = render_template("email/email_template.html", title=subject, msg_list=msg_list, buttons=[button]).encode('utf-8')
    msg.html = html

    try:
        mail.send(msg)
    except Exception as e:
        print("**MAIL_ERROR**")
        print(e)

def send_reset_email(user):
    """
        Sends an email to user with a link with temporary
        token to reset their password.

        user: User
    """
    token = user.get_reset_token(expires_in=1800)
    msg = Message("TapeFlip.app -- Password Reset Request", sender="reelone@tapeflip.app", recipients=[user.email])
    url = url_for("bp_users.password_reset", token=token, _external=True)
    html = render_template("email/password_reset.html", url=url).encode('utf-8')
    msg.html = html
    mail.send(msg)
