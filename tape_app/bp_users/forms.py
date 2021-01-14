from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from tape_app.models import User, FreeCreditCode

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number (optional), Please include country code (ie: +1 in USA/Canada)',validators=[])
    text_notif = BooleanField("Recieve text notifications", render_kw={"data-toggle":"toggle"})
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
            Checks if username is already talen.
        """
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        else:
            for char in username.data:
                if not (char.isalnum() or char in [".","_","-"]):
                    raise ValidationError('Please choose a username that only contains numbers, letters, hyphens (-), periods (.), or underscores (_).')

    def validate_email(self, email):
        """
            Checks if email is already talen.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number',validators=[DataRequired()])
    text_notif = BooleanField("Recieve text notifications", render_kw={"data-toggle": "toggle"})
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """
            Checks if username is already taken.
        """
        if username.data.lower() != current_user.username.lower():
            user = User.query.filter_by(username=username.data.lower()).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
            else:
                for char in username.data:
                    if not (char.isalnum() or char in [".","_","-"]):
                        raise ValidationError('Please choose a username that only contains numbers, letters, hyphens (-), periods (.), or underscores (_).')

    def validate_email(self, email):
        """
            Checks if email is already talen.
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        """
            Checks if email is already talen.
        """
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class AddCreditsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    num_of_credits = StringField('Number of Credits', validators=[DataRequired(), Length(min=1, max=3)])
    submit = SubmitField('Give Credits')

    def validate_username(self, username):
        """
            Checks if username exists.
        """
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is None:
            raise ValidationError('There is no account with that username.')

class CompleteSessionForm(FlaskForm):
    zip_file = FileField('Upload ZIP', validators=[FileAllowed(['zip'])])
    submit = SubmitField('Complete Session')


class FreeCreditCodeForm(FlaskForm):
    num_of_credits = StringField('Number of Credits', validators=[DataRequired(), Length(min=2, max=4)])
    num_of_codes = StringField('Number of Codes', validators=[DataRequired(), Length(min=1, max=2)])
    prefix = StringField('Prefix to code', validators=[Length(min=1, max=15)])
    submit = SubmitField('Create Code(s)')

class RedeemForm(FlaskForm):
    code = StringField('Enter Code', validators=[DataRequired()])
    submit = SubmitField('Redeem Code')

    def validate_code(self, code):
        """
            Checks if code exists.
        """
        c = FreeCreditCode.query.filter_by(code=code.data).first()
        if c is None:
            raise ValidationError("That code doesn't exist.")
