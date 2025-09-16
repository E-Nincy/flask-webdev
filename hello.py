from flask import Flask

app = Flask(__name__)

# --- Home Page ---
@app.route('/')
def home():
    return '''
    <h2>Welcome to My Mini Site!</h2>
    <p>Check out the other pages:</p>
    <ul>
        <li><a href="/about">About Me</a></li>
        <li><a href="/songs">My Favorite Songs</a></li>
    </ul>
    '''

# --- About Page ---
@app.route('/about')
def about():
    return '''
    <h2>About Me</h2>
    <p>Hi! I'm Nin, currently learning Python and web development.
    I hope to become really confident building full-stack web apps by the end of this course. 
    I love coding, coffee, and anything tech!</p>
    '''

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

# --- Dynamic Route: Greet with name and age ---
@app.route('/greet/<name>/<age>')
def greet(name, age):
    return f"Hello, {name}! You are {age} years old."

# --- Dynamic Route: Square a number ---
@app.route('/square/<int:number>')
def square(number):
    return f"The square of {number} is {number**2}."

# --- Dynamic Route: Shout text (with spaces) ---
@app.route('/shout/<text>')
def shout(text):
    text = text.replace("-", " ")
    return f"You shouted: {text.upper()}!"

# --- Run the app ---
if __name__ == '__main__':
    app.run(debug=True)

