from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField, EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('email@example.com', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class NewList(FlaskForm):
    title = StringField('New List Title', validators=[DataRequired()])
    submit = SubmitField('Create List')


class TaskForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    date_tbc = DateTimeField('To Be Completed By...')
    submit = SubmitField('Add Task')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('email@example.com', validators=[DataRequired()])
    password = PasswordField('Create Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Join Us...')
