import os
from werkzeug.utils import secure_filename
from flask import current_app as app
import soundfile as sf

def save_audio_file(file, sound_num, session_id, user_id, zip=False):
    """
        Saves session audio files to user's own directory in /protected

        file: file
        sound_num: int
        session_id: int
        user_id: int
    """
    # get a secure file name
    filename = secure_filename(file.filename)

    if filename == '':  # secure file name could be empty
        f_ext = os.path.splitext(file.filename)
        if zip:
            filename = 'Session_' + str(session_id) + "_Completed" + f_ext
        else:
            filename = 'Session_' + str(session_id) + "_Sound_" + str(sound_num) + f_ext

    # get path to user's folder
    users_folder = os.path.join(app.root_path, 'protected', "USR_" + str(user_id))

    # if it doesn't exist yet create it
    if not os.path.exists(users_folder):
        os.mkdir(users_folder)

    # save to file system at user's path
    file.save(os.path.join(users_folder, filename))

    return filename


def get_sound_credits(sound, user_id):
    """
        Get's a sound's appropriate credit value by looking at it's
        length and options selected.

        sound: Sound
        user_id: int
    """

    # get user's path
    file_path = os.path.join(app.root_path, 'protected', "USR_" + str(user_id), sound.file_name)

    sound_file = sf.SoundFile(file_path)
    dur = int(len(sound_file) / sound_file.samplerate)
    credits = 0

    if dur <= 30:
        credits += 3
    elif dur > 30 and dur <= 60:
        credits += 6
    elif dur > 60 and dur <= 120:
        credits += 12
    elif dur >= 120:
        credits += 15

    # if sound.options != 'Normal-Speed':
    #     credits += 2

    return credits
