from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class EventConfigForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired(), Length(min=1, max=100)])
    api_key = StringField('API Key', validators=[DataRequired(), Length(min=1, max=256)])
    webhook_secret = StringField('Webhook Secret', validators=[DataRequired(), Length(min=1, max=256)])
    submit = SubmitField('Save Configuration')
