import binascii
import os
from PIL import Image
from flask import current_app as app

def clean_phone_number(phone_number_data):
    """
        Removes all chars from phone_number that isnt a number.

        phone_number_data: unicode
    """
    phone_number_string = str(phone_number_data)

    clean_phone_number = ""

    for char in phone_number_string:
        if char in ["1","2","3","4","5","6","7","8","9","0"]:
            clean_phone_number = clean_phone_number + char

    return clean_phone_number


def save_picture(form_picture):
    """
        Saves an avi.

        form_picture: file
    """
    # get a random number string
    random_hex = str(binascii.hexlify(os.urandom(8)))

    # get file ext
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # get path of picture
    picture_path = os.path.join(app.root_path, 'static/images/avi', picture_fn)

    # resive image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # save image file to file system at picture_path
    i.save(picture_path)
    return picture_fn
