from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)

bootstrap = Bootstrap(app)

# --- Home Page ---
@app.route('/')
def home():
    favorite_songs = ["Bohemian Rhapsody", "Blinding Lights", "Chiquitita"]
    user = "Nin"           # <-- make sure this exists
    bad_song = "Baby Shark" # optional
    return render_template(
        'index.html',
        user=user,
        favorite_songs=favorite_songs,
        bad_song=bad_song
    )
# --    EXAMPLE → http://127.0.0.1:5000/


# --- About Page ---
@app.route('/about')
def about():
    return '''
    <h2>About Me</h2>
    <p>Hi! I'm Nin, currently learning Python and web development.
    I hope to become really confident building full-stack web apps by the end of this course. 
    I love coding, coffee, and anything tech!</p>
    '''
# --    EXAMPLE → http://127.0.0.1:5000/about

# --- Favorite Songs Page ---
@app.route('/songs')
def songs():
    favorite_songs = ["Bohemian Rhapsody", "Blinding Lights", "Chiquitita"]
    return render_template('index.html', user="Nin", favorite_songs=favorite_songs)
# --    EXAMPLE → http://127.0.0.1:5000/songs

# --- Dynamic Route: Greet with name and age ---
@app.route('/greet/<name>/<age>')
def greet(name, age):
    return f"Hello, {name}! You are {age} years old."
# --    EXAMPLE → http://127.0.0.1:5000/greet/Nin/25

# --- Dynamic Route: Square a number ---
@app.route('/square/<int:number>')
def square(number):
    return f"The square of {number} is {number**2}."
# --    EXAMPLE → http://127.0.0.1:5000/square/5

# --- User ---
@app.route('/user/<username>')
def user(username):
    return render_template("user.html", username=username)
# --    EXAMPLE → http://127.0.0.1:5000/user/nin

# --- Dynamic Route: Shout text (with spaces) ---
@app.route('/shout/<text>')
def shout(text):
    text = text.replace("-", " ")
    return f"You shouted: {text.upper()}!"
# --    EXAMPLE → http://127.0.0.1:5000/shout/hello-world

# Temporary route for viewing and debugging base template
@app.route('/base')
def base_temp():
    return render_template("base.html")

# Temporary route for *recreating* the index template using blocks
@app.route('/index2')
def index2_temp():
    favorite_songs = ["Bohemian Rhapsody", "Blinding Lights", "Chiquitita"]
    user = "Nin"
    bad_song = "Baby Shark"
    return render_template(
        "index2.html",
        user=user,
        favorite_songs=favorite_songs,
        bad_song=bad_song
    )

@app.route('/derived')
def derived():
    return render_template('derived.html')
# --    EXAMPLE → http://127.0.0.1:5000/derived

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)

