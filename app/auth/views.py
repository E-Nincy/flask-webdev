from flask import render_template, redirect, url_for, flash
from . import auth
from .forms import RegistrationForm, LoginForm
from .. import db
from ..models import User
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, logout_user, login_required, current_user


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.password = form.password.data 

        db.session.add(user)
        try:
            db.session.commit()
            flash("✅ Registration successful! You can log in now.", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("❌ Email already registered, please choose another.", "danger")

    return render_template("auth/register.html", form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_entered = form.email.data
        user = User.query.filter_by(email=email_entered).first()
        if not user:
            user = User(username=email_entered.split('@')[0], email=email_entered)
            db.session.add(user)
            db.session.commit()
            flash("Account created!", "success")
        else:
            flash("Welcome back!", "success")
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.home'))
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out successfully", "success")
    return redirect(url_for('main.home'))