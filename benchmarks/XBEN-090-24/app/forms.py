from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=1, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=64)])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class AppointmentForm(FlaskForm):
    event_date = DateField('Appointment Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = StringField('Start Time', validators=[DataRequired()])
    duration = SelectField('Duration (minutes)', choices=[('15', '15'), ('30', '30'), ('45', '45'), ('60', '60')], default='30')
    category = SelectField('Visit Type', choices=[
        ('Office Visit', 'Office Visit'),
        ('Follow Up', 'Follow Up'),
        ('Annual Physical', 'Annual Physical'),
        ('Consultation', 'Consultation'),
        ('Lab Work', 'Lab Work'),
    ], default='Office Visit')
    provider_id = SelectField('Provider', coerce=int, validators=[DataRequired()])
    comments = TextAreaField('Comments / Reason for Visit', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Appointment')


class CancelForm(FlaskForm):
    reason = TextAreaField('Cancellation Reason', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Cancel Appointment')
