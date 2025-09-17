from flask import Flask, render_template

app = Flask(__name__)

# --- Home Page ---
@app.route('/')
def home():
    return render_template('index.html')
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
    return '''
    <h2>My Favorite Songs</h2>
    <ul>
        <li><strong>Bohemian Rhapsody</strong> - Queen</li>
        <li><strong>Blinding Lights</strong> - The Weeknd</li>
        <li><strong>Chiquitita</strong> - ABBA</li>
    </ul>
    '''
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

# --- Dynamic Route: Shout text (with spaces) ---
@app.route('/shout/<text>')
def shout(text):
    text = text.replace("-", " ")
    return f"You shouted: {text.upper()}!"
# --    EXAMPLE → http://127.0.0.1:5000/shout/hello-world

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)

