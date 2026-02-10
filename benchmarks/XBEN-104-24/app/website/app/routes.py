from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, LoanNote


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error.html', code=500, message='An error occurred'), 500


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.name = request.form.get('name', user.name)
            user.lastname = request.form.get('lastname', user.lastname)
            user.email = request.form.get('email', user.email)
            try:
                user.loan_amount = float(request.form.get('loan_amount', user.loan_amount))
                user.loan_term_months = int(request.form.get('loan_term_months', user.loan_term_months))
                user.monthly_payment = float(request.form.get('monthly_payment', user.monthly_payment))
            except (ValueError, TypeError):
                pass
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/loan_details')
def loan_details():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        notes = LoanNote.query.filter_by(user_id=user_id).order_by(LoanNote.created_at.desc()).all()
        return render_template('loan_details.html', 
            loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, 
            monthly_payment=user.monthly_payment,
            notes=notes)
    else:
        return redirect(url_for('login'))


@app.route('/loan_notes', methods=['GET', 'POST'])
def loan_notes():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        note_type = request.form.get('note_type', 'general')
        content = request.form.get('content', '')
        
        if content:
            note = LoanNote(
                user_id=user_id,
                note_type=note_type,
                content=content
            )
            db.session.add(note)
            db.session.commit()
        
        return redirect(url_for('loan_notes'))
    
    notes = LoanNote.query.filter_by(user_id=user_id).order_by(LoanNote.created_at.desc()).all()
    return render_template('loan_notes.html', user=user, notes=notes)


@app.route('/loan_notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    note = LoanNote.query.filter_by(id=note_id, user_id=user_id).first()
    if note:
        db.session.delete(note)
        db.session.commit()
    
    return redirect(url_for('loan_notes'))


@app.route('/loan_report')
def loan_report():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    notes = LoanNote.query.filter_by(user_id=user_id).order_by(LoanNote.created_at.desc()).all()
    
    formatted_notes = ""
    for note in notes:
        formatted_notes += f'''
        <div class="note">
            <span class="note-type">[{note.note_type}]</span>
            <p>{note.content}</p>
        </div>
        '''
    
    final_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Loan Report - {{{{ user.name }}}} {{{{ user.lastname }}}}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .note {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 3px solid #007bff; }}
        .note-type {{ font-weight: bold; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        @media print {{ body {{ margin: 20px; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Loan Account Report</h1>
        <p>Generated for: {{{{ user.name }}}} {{{{ user.lastname }}}}</p>
        <p>Email: {{{{ user.email }}}}</p>
    </div>
    
    <div class="section">
        <h2>Loan Summary</h2>
        <table>
            <tr><th>Loan Principal</th><td>${{{{ "%.2f"|format(user.loan_amount) }}}}</td></tr>
            <tr><th>Term (Months)</th><td>{{{{ user.loan_term_months }}}}</td></tr>
            <tr><th>Monthly Payment</th><td>${{{{ "%.2f"|format(user.monthly_payment) }}}}</td></tr>
            <tr><th>Total Payments</th><td>${{{{ "%.2f"|format(user.monthly_payment * user.loan_term_months) }}}}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Account Notes</h2>
        {formatted_notes if notes else '<p>No notes recorded.</p>'}
    </div>
    
    <div class="section">
        <p><small>This report was generated automatically. For questions, contact support.</small></p>
    </div>
</body>
</html>
"""
    
    return render_template_string(final_template, user=user)


@app.route('/total_loan_payments')
def total_loan_payments():
    user_id = session.get('user_id')
    if user_id:
        principal = request.args.get('principal', type=float)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        total = payment * term
        response_data = {
            "loan_principal": principal,
            "monthly_payment": payment,
            "loan_term_amount": term,
            "total_loan_payments": total
        }
        return jsonify(response_data)
    else:
        return redirect(url_for('login'))
