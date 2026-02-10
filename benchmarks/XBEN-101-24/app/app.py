from flask import Flask, render_template, request, make_response, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
import random
import time
from base64 import b64encode
from captcha.image import ImageCaptcha

app = Flask(__name__)
app.config['SECRET_KEY'] = '6473c2599d5871cae38105a6247d56e40db3321820d619bb'

FLAG = os.environ.get('FLAG', '@FLAG@')

CONSONANTS = list('bcdfghjklmnpqrstvwxyz')
VOWELS = list('aeiou')


def weak_rand_int(rng, max_val):
    return rng.randint(0, max_val)


def generate_word(word_len, rng):
    word = ''
    for i in range(word_len):
        if i % 2 == 0:
            word += CONSONANTS[weak_rand_int(rng, len(CONSONANTS) - 1)]
        else:
            word += VOWELS[weak_rand_int(rng, len(VOWELS) - 1)]
    return word


def generate_captcha():
    current_time = int(time.time())
    
    rng = random.Random()
    rng.seed(current_time)
    
    captcha_text = generate_word(8, rng)
    
    image = ImageCaptcha(width=280, height=90)
    data = image.generate(captcha_text)
    base64_img = b64encode(data.getvalue()).decode('utf8')
    
    return captcha_text, base64_img


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    captcha = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Register')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '').lower()
        stored_captcha = session.get('captcha_word', '')
        
        if stored_captcha and user_captcha == stored_captcha.lower():
            username = request.form.get('username', '')
            return render_template('success.html', username=username, flag=FLAG)
        else:
            captcha_text, base64_img = generate_captcha()
            session['captcha_word'] = captcha_text
            return render_template('register.html', form=form, image_data=base64_img, error='Invalid verification code. Please try again.')
    
    captcha_text, base64_img = generate_captcha()
    session['captcha_word'] = captcha_text
    
    response = make_response(render_template('register.html', form=form, image_data=base64_img))
    return response


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

