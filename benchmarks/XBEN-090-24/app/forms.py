from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DraftForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save Draft')

class ChangePasswordForm(FlaskForm):
    username = HiddenField('Username')
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
