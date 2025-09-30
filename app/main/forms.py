from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError
from ..models import User, Role

class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    email = StringField("Your Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

class ZodiacForm(FlaskForm):
    birthdate = DateField("Enter your birthdate", validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField("Find my sign!")

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0,64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

class AdminLevelEditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int) 
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    bio = TextAreaField('Bio')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # populate role choices dynamically
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')