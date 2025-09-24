from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Email

class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

class ZodiacForm(FlaskForm):
    birthdate = DateField("Enter your birthdate", validators=[DataRequired()], format='%Y-%m-%d')