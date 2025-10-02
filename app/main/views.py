from flask import session, render_template, redirect, url_for, flash, request, current_app
from . import main
from .forms import NameForm, ZodiacForm, EditProfileForm, AdminLevelEditProfileForm, CompositionForm
from .. import db
from ..models import Role, User, Permission, Composition
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
    form = CompositionForm()
    if current_user.can(Permission.PUBLISH) and form.validate_on_submit():
        composition = Composition(
            release_type=form.release_type.data,
            title=form.title.data,
            description=form.description.data,
            artist=current_user._get_current_object()
        )
        db.session.add(composition)
        db.session.commit()
        flash("Composition published successfully!", "success")
        return redirect(url_for('.home'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config.get('RAGTIME_COMPS_PER_PAGE'),
        error_out=False
    )
    compositions = pagination.items


    return render_template(
        'index.html',
        form=form,
        compositions=compositions,
        pagination=pagination
    )

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
    return render_template('about.html')


@main.route('/songs', methods=['GET', 'POST'])
def songs():
    form = CompositionForm()
    if current_user.is_authenticated and current_user.can(Permission.PUBLISH) and form.validate_on_submit():
        composition = Composition(
            release_type=form.release_type.data,
            title=form.title.data,
            description=form.description.data,
            artist=current_user._get_current_object()
        )
        db.session.add(composition)
        db.session.commit()
        flash("Your composition has been published!", "success")
        return redirect(url_for('.songs'))

    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
        page=page,
        per_page=current_app.config.get('RAGTIME_COMPS_PER_PAGE'),
        error_out=False
    )
    compositions = pagination.items


    return render_template(
        'index.html',
        form=form,
        compositions=compositions,
        pagination=pagination
    )


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