from flask import session, render_template, redirect, url_for, flash
from . import main
from .forms import NameForm, ZodiacForm, EditProfileForm, AdminLevelEditProfileForm
from .. import db
from ..models import Role, User, Permission
from flask_login import login_required, login_user, current_user
from ..decorators import admin_required, permission_required

def admin_required(f):
    """Decorator that ensures only the admin can access."""
    from functools import wraps
    from flask import abort
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_administrator():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/', methods=['GET', 'POST'])
def home():
    """Home page: handle user name and email input."""
    form = NameForm()
    if form.validate_on_submit():
        name_entered = form.name.data
        email_entered = form.email.data
        user_by_name = User.query.filter_by(username=name_entered).first()
        user_by_email = User.query.filter_by(email=email_entered).first()

        if user_by_name:
            session['known'] = True
            session['name'] = name_entered
            flash("Welcome back!", "success")
        elif user_by_email:
            flash("This email is already registered. Please use another email.", "warning")
            return redirect(url_for('.home'))
        else:
            # Create the user if does not exist
            user = User(username=name_entered, email=email_entered)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            session['name'] = name_entered
            flash("Great! We hope you enjoy the community", "success")

        form.name.data = ''
        form.email.data = ''
        return redirect(url_for('.home'))

    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))

@main.route('/top-secret')
@login_required
def top_secret():
    return "Welcome, VIP member! "\
           "You have exclusive access to this page. "\
           "Now let me get your cocktail."

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

# --- About ---
@main.route('/about')
def about():
    return '''
    <h2>About Me</h2>
    <p>Hi! I'm currently learning Python and web development.
    I hope to become really confident building full-stack web apps by the end of this course.
    I love coding, coffee, and anything tech!</p>
    '''

# --- Songs ---
@main.route('/songs', methods=['GET', 'POST'])
def songs():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        flash(f"Great! Welcome, {form.name.data}!", "success")
        return redirect(url_for('.songs'))
    favorite_songs = ["Bohemian Rhapsody", "Blinding Lights", "Chiquitita"]
    bad_song = "Baby Shark"
    return render_template('index.html', form=form, name=session.get('name'),
                           favorite_songs=favorite_songs, bad_song=bad_song)

# --- User profile ---
#@main.route('/user/<username>')
#def user_profile(username):
    #return render_template("user.html", username=username)#

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated your profile! Looks great.', 'success')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form)

@main.route('/editprofile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    user = User.query.get_or_404(id)
    form = AdminLevelEditProfileForm(user=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.bio = form.bio.data
        db.session.commit()
        flash('The profile has been updated by the admin!', 'success')
        return redirect(url_for('.user_profile', username=user.username))

    # Pre-fill the form
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.bio.data = user.bio

    return render_template('admin_edit_profile.html', form=form, user=user)

# --- Zodiac functions ---
def get_zodiac_sign(month, day):
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "Pisces"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"

def get_chinese_zodiac(year):
    animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
               "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    return animals[year % 12]

# --- Zodiac page ---
@main.route('/zodiac', methods=['GET', 'POST'])
def zodiac():
    form = ZodiacForm()
    if form.validate_on_submit():
        birthdate = form.birthdate.data
        western = get_zodiac_sign(birthdate.month, birthdate.day)
        chinese = get_chinese_zodiac(birthdate.year)
        flash(f"Your Western Zodiac sign is {western} and your Chinese Zodiac animal is {chinese}!", "warning")
        return redirect(url_for('.zodiac'))
    return render_template('zodiac.html', form=form)

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "Welcome, administrator!"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "Greetings, moderator!"