# This file contains all the text that is sent in any email/text notifications

def registerd_msg(user):
    msg = "Whats up 🔥{}🔥\n\nWelcome to TapeFlip.app. Thanks you for making an account!\n\nTo start hearing your sounds on tape, create a session at the link below and upload your audio files.".format(user.username)
    return msg

def complete_session_msg(session):
    msg = "Ayo 🔥{}🔥\n\nThe files from your session '{}' are all done. To download them follow the link below and click the 'Download your files' button on the bottom right of the page.\n\nThanks for creating a session on TapeFlip.app, we hope you love the real tape sound!".format(session.user.username, session.session_name)
    return msg
