from flask import render_template, redirect, url_for, flash, request, current_app
from . import auth
from .forms import RegistrationForm, LoginForm, ChangeEmailForm, ChangePasswordForm
from .. import db
from ..models import User
from ..email import send_email   # <- import the email sending function
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new user instance
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.password = form.password.data 

        db.session.add(user)
        try:
            db.session.commit()

            # 🔹 Generar token
            token = user.generate_confirmation_token()
            
            # 🔹 Send confirmation email
            send_email(
                to=user.email,
                subject="Please confirm your account",
                template="auth/email/confirm",   # look for confirm.html y confirm.txt
                user=user,
                token=token
            )

            # 🔹 Send a notification email to the admin about the new user
            admin_email = current_app.config.get('RAGTIME_ADMIN')
            send_email(
                to=admin_email,
                subject="New user registered",
                template="mail/new_user",  # looks for new_user.html and new_user.txt in templates/mail/
                user=user,
                time=datetime.utcnow()
            )

            flash("✅ Registration successful! Please check your email to confirm your account.", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("❌ Email already registered, please choose another.", "danger")

    # Render the registration page with the form
    return render_template("auth/register.html", form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(email=email_entered).first()
        if user and check_password_hash(user.password_hash, password_entered):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page is None or not next_page.startswith('/'):
                next_page = url_for('main.home')
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(next_page)
        else:
            flash("Invalid email or password.", "danger")  # mensaje de error

    return render_template('auth/login.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
        current_user.password = form.new_password.data
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('auth/change_password.html', form=form)

# --- Change email ---
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.new_email.data
        db.session.commit()
        flash('Your email has been updated!', 'success')
        return redirect(url_for('main.user', username=current_user.username))
    return render_template('auth/change_email.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out successfully", "success")
    return redirect(url_for('main.home'))

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash("You're already confirmed, silly!")
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()

        send_email(
            to=current_user.email,
            subject="Welcome to our App!",
            template="mail/welcome",
            user=current_user
        )

        flash('You have confirmed your account! Thank you.')
    else:
        flash("Whoops! That confirmation link either expired, or it isn't valid.")
    return redirect(url_for('main.home'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('auth/unconfirmed.html')

@auth.route('/resend-confirmation')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        flash("Your account is already confirmed.", "info")
        return redirect(url_for('main.home'))

    token = current_user.generate_confirmation_token()
    send_email(
        to=current_user.email,
        subject="Please confirm your account",
        template="auth/email/confirm",
        user=current_user,
        token=token
    )
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for('auth.unconfirmed'))

