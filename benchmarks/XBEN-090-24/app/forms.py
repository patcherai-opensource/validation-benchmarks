from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[Optional(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published')])
    submit = SubmitField('Save Article')

class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[Optional(), Length(max=120)])
    bio = TextAreaField('Bio', validators=[Optional()])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    username = HiddenField('Username')
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')
