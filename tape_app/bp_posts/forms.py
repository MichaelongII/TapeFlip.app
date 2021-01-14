from flask_wtf import FlaskForm
from wtforms import Form, FieldList, FormField, StringField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class SoundForm(Form):
    """
        Subform.
        CSRF is disabled for this subform (using `Form` as parent class) because
        it is never used by itself.

    """

    file_name = FileField('Select Audio File', validators=[DataRequired(), FileAllowed(['wav', 'mp3'])])
    options = SelectField('Speed (Reel 2 Reel only)', choices=[("Normal-Speed", "Normal-Speed"), ("Half-Speed", "Half-Speed"), ("Double-Speed", "Double-Speed")])
    machine = SelectField('Tape Machine', choices=[("Teac A-2300s (Reel 2 Reel)", "Teac A-2300s (Reel 2 Reel)"), ("Sony TC-K35 (Cassette)", "Sony TC-K35 (Cassette)")])

class SessionForm(FlaskForm):
    """
        Parent form.
    """
    session_name = StringField('Session Name', validators=[DataRequired(), Length(min=1, max=40)])
    sounds = FieldList(
        FormField(SoundForm),
        min_entries=1,
        max_entries=20
    )
