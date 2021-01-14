from flask import Blueprint, jsonify
from flask import current_app as app
from flask import url_for, flash, redirect, request
from tape_app import db, bcrypt
from tape_app.bp_users.forms import RegistrationForm, LoginForm, \
    UpdateAccountForm, ResetPasswordForm, RequestResetForm, RedeemForm
from tape_app.models import User, Session, FreeCreditCode
from tape_app.bp_users.utils import clean_phone_number, save_picture
from flask_login import login_user, current_user, logout_user, login_required
from tape_app.utils import render_page
from tape_app.bp_mail.email_utils import send_email, send_reset_email
from tape_app.bp_mail.messages import registerd_msg
import paypalrestsdk

bp_users = Blueprint("bp_users", __name__)

@bp_users.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    """
        The current user's profile giving them a list of all
        their sessions and the option to update their information.
    """
    users_sessions = Session.query.filter_by(user_id=current_user.id)
    page = request.args.get('page', 1, type=int)

    sessions_paginated = users_sessions\
        .order_by(Session.date_posted.desc())\
        .paginate(page=page, per_page=6)

    return render_page('user/profile.html', title='Profile',page=page, sessions=sessions_paginated)

@bp_users.route("/login", methods=['GET', 'POST'])
def login():
    """
        Logs user in.
    """
    # if user is already logged in redirect them home
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        # get user by email
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # compare given password hash to stored password hash
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            if user.role == "user":
                return redirect(url_for('bp_main.home'))
            elif user.role == "admin":
                return redirect(url_for('bp_admin.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_page('public/login.html', title='Login', form=form)


@bp_users.route("/register", methods=['GET', 'POST'])
def register():
    """
        Creates a new user.
    """
    # if user is already logged in redirect them home
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # generate password hash
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # create user
        user = User(username=form.username.data.lower(), email=form.email.data.lower(),
                    phone_number=clean_phone_number(form.phone_number.data), password=hashed_password, text_notif=form.text_notif.data)
        db.session.add(user)
        db.session.commit()

        # send welcome email
        send_email(subject="Welcome!",
                    msg_body=registerd_msg(user),
                    button=("Create a Session", url_for('bp_posts.new_session')),
                    recipient=user)
        flash('Thanks for signing up! You are now able to log in', 'success')
        return redirect(url_for('bp_users.login'))

    return render_page('public/register.html', title='Register', form=form)

@bp_users.route("/logout")
def logout():
    """
        Loggs user out.
    """
    logout_user()
    return redirect(url_for('bp_main.home'))

@bp_users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    """
        Sends an email to user allowing them to reset their password.
    """
    # if user is already logged in redirect them home
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))

    form = RequestResetForm()
    if form.validate_on_submit():
        # get user by email
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # send user an email with reset token
        send_reset_email(user)

        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('bp_users.login'))

    return render_page('public/reset_request.html', title='Reset PW', form=form)


@bp_users.route("/password_reset/<token>", methods=['GET', 'POST'])
def password_reset(token):
    """
        Resets user's password provided the token parameter is a valid token.
    """
    # if user is already logged in redirect them home
    if current_user.is_authenticated:
        return redirect(url_for('bp_main.home'))

    # verify token
    user = User.verify_reset_token(token)
    if not user:  # token in not valid
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('bp_users.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # generate passowrd hash
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # update user's password
        user.password = hashed_password
        db.session.commit()

        flash('Your password has been reset.', 'success')
        return redirect(url_for('bp_users.login'))

    return render_page('public/reset_token.html', title='Reset PW', form=form)

@bp_users.route("/update_account", methods=['GET', 'POST'])
@login_required
def update_account():
    """
        Form to update information of an User.
    """

    form = UpdateAccountForm()
    if form.validate_on_submit():

        # assign new data for user
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        current_user.username = form.username.data.lower()
        current_user.email = form.email.data
        current_user.phone_number = form.phone_number.data
        current_user.text_notif = form.text_notif.data
        db.session.commit()

        flash('Your account has been updated!', 'success')
        return redirect(url_for('bp_users.profile'))

    elif request.method == 'GET':
        # fill in form
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone_number.data = current_user.phone_number
        form.text_notif.data = current_user.text_notif

    image_file = url_for('static', filename='images/avi/' + current_user.image_file)
    return render_page('user/update_account.html', title='Profile Info', image_file=image_file, form=form)


@bp_users.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    """
        Form to give creits to a user.
    """

    form = RedeemForm()

    if form.validate_on_submit():
        code_obj = FreeCreditCode.query.filter_by(code=form.code.data).first()
        current_user.credits += code_obj.credits
        db.session.commit()
        db.session.delete(code_obj)
        db.session.commit()

        return redirect(url_for('bp_users.profile'))

    return render_page('user/redeem.html', title='Redeem Code', form=form)

@bp_users.route('/checkout/<string:num_of_credits>', methods=['GET', 'POST'])
@login_required
def checkout(num_of_credits):
    """
        Checkout page that has paypal button.
    """
    price = None
    # get pricing oftion with same credits value as num_of_credits
    for option in app.config["PRICING_OPTIONS"]:
        if num_of_credits == option.credits:
            price = option.price
            break

    if price is None:
        return redirect('bp_main.pricing')

    return render_page('user/checkout.html', price=price, num_of_credits=int(num_of_credits), title='Checkout')


@bp_users.route("/create_payment/<int:price>/<int:num_of_credits>", methods=['GET', 'POST'])
def create_payment(price, num_of_credits):
    """
        Creates a Paypal payment object for the amount of 'price'

        price: int
        num_of_credits: int
    """

    description = "Purchase of " + str(num_of_credits) + " Credits from TapeFlip.app"
    paypalrestsdk.configure({
        "mode": app.config["PAYPAL_MODE"],  # sandbox or live
        "client_id": app.config["PAYPAL_CLIENT_ID"],
        "client_secret": app.config["PAYPAL_CLIENT_SECRET"]})

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": url_for('bp_users.profile'),
            "cancel_url": url_for('bp_users.profile')},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Credit Purchase",
                    "price": price,
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": price,
                "currency": "USD"},
            "description": description}]})

    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)

    return jsonify({"paymentID":payment.id})


@bp_users.route("/execute_payment/<int:num_of_credits>", methods=['GET', 'POST'])
@login_required
def execute_payment(num_of_credits):
    """
        Exceutes a Paypal payment

        num_of_credits: int
    """
    # get payment by paymentID
    payment = paypalrestsdk.Payment.find(request.form["paymentID"])

    if payment.execute({"payer_id":request.form["payerID"]}):
        current_user.credits += num_of_credits
        db.session.commit()
        return redirect(url_for('bp_posts.new_session'))
    else:
        print(payment.error)
        flash("There was an error processing your payment, please try again later.", "danger")
        return redirect(url_for('bp_users.profile'))
