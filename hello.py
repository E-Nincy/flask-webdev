from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect, url_for, session, flash, abort
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") 
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

# --- Form ---
class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

# --- Home / Index Page ---
@app.route('/', methods=['GET', 'POST'])
def home():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        flash(f"Great! Welcome, {form.name.data}!")
        return redirect(url_for('home'))
    return render_template('index.html', form=form, name=session.get('name'))

# --- About Page ---
@app.route('/about')
def about():
    return '''
    <h2>About Me</h2>
    <p>Hi! I'm Nin, currently learning Python and web development.
    I hope to become really confident building full-stack web apps by the end of this course. 
    I love coding, coffee, and anything tech!</p>
    '''

# --- Favorite Songs Page  ---
@app.route('/songs', methods=['GET', 'POST'])
def songs():
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        flash(f"Great! Welcome, {form.name.data}!")
        return redirect(url_for('songs'))
    favorite_songs = ["Bohemian Rhapsody", "Blinding Lights", "Chiquitita"]
    bad_song = "Baby Shark"
    return render_template('index.html', form=form, name=session.get('name'),
                           favorite_songs=favorite_songs, bad_song=bad_song)

# --- Dynamic Route: Greet with name and age ---
@app.route('/greet/<name>/<age>')
def greet(name, age):
    return f"Hello, {name}! You are {age} years old."

# --- Dynamic Route: Square a number ---
@app.route('/square/<int:number>')
def square(number):
    return f"The square of {number} is {number**2}."

# --- User Profile ---
@app.route('/user/<username>')
def user(username):
    return render_template("user.html", username=username)

# --- Dynamic Route: Shout text ---
@app.route('/shout/<text>')
def shout(text):
    text = text.replace("-", " ")
    return f"You shouted: {text.upper()}!"

# --- Zodiac ---
class ZodiacForm(FlaskForm):
    birthdate = DateField("Enter your birthdate", validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField("Submit")

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
    animals = ["Monkey", "Rooster", "Dog", "Pig", "Rat", "Ox", 
               "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat"]
    return animals[year % 12]

# --- Route /zodiac ---
@app.route('/zodiac', methods=['GET', 'POST'])
def zodiac():
    form = ZodiacForm()
    if form.validate_on_submit():
        birthdate = form.birthdate.data
        western = get_zodiac_sign(birthdate.month, birthdate.day)
        chinese = get_chinese_zodiac(birthdate.year)
        flash(f"Your Western Zodiac sign is {western} and your Chinese Zodiac animal is {chinese}!")
        return redirect(url_for('zodiac'))
    return render_template('zodiac.html', form=form)

# --- Error Handlers ---
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_title="Forbidden",
                           error_msg="You shouldn't be here!"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_title="Not Found",
                           error_msg="That page doesn't exist"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_title="Internal Server Error",
                           error_msg="Sorry, we seem to be experiencing technical difficulties"), 500

# --- Run App ---
if __name__ == '__main__':
    app.run(debug=True)
