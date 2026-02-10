from flask import Flask, render_template, request, redirect, url_for, flash, session
from jinja2 import Template, Environment, FileSystemLoader, BaseLoader
import os

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(24)

# Default notification template - simulating Spring Boot Admin's MailNotifier template
DEFAULT_NOTIFICATION_TEMPLATE = """
<div class="notification">
    <h3>Application Status Update</h3>
    <p>Dear {{ applicant_name }},</p>
    <p>Your application status: {{ status }}</p>
    <p>Thank you for your interest in Swift Shipping & Transport Inc.</p>
</div>
"""

# Global template storage - simulating configurable mail template path like Spring Boot Admin
notification_templates = {
    'default': DEFAULT_NOTIFICATION_TEMPLATE
}

# Store the current active template name
current_template = 'default'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/application')
def application():
    return render_template('application.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    return render_template('thank_you.html', 
                          rendered_template=f'Thank you {name} for your submission.')

# Admin panel for notification template configuration
# Simulates Spring Boot Admin's ability to configure mail template
@app.route('/admin')
def admin():
    return render_template('admin.html', 
                          templates=notification_templates,
                          current_template=current_template)

@app.route('/admin/templates')
def list_templates():
    return render_template('template_list.html',
                          templates=notification_templates,
                          current_template=current_template)

# Endpoint to set/configure notification template - similar to setting spring.boot.admin.notify.mail.template
@app.route('/admin/templates/configure', methods=['POST'])
def configure_template():
    global current_template
    template_name = request.form.get('template_name', 'default')
    template_content = request.form.get('template_content', '')
    
    if template_content:
        # Store the custom template - this simulates being able to control the template path/content
        notification_templates[template_name] = template_content
    
    current_template = template_name
    flash(f'Template "{template_name}" configured successfully!', 'success')
    return redirect(url_for('admin'))

# Preview/test the notification template - this is where the SSTI vulnerability exists
# Similar to how MailNotifier.getBody() processes templates in Spring Boot Admin
@app.route('/admin/templates/preview', methods=['POST'])
def preview_template():
    template_name = request.form.get('template_name', current_template)
    
    # Get the template content
    template_content = notification_templates.get(template_name, DEFAULT_NOTIFICATION_TEMPLATE)
    
    # Sample data for preview
    preview_data = {
        'applicant_name': 'Test Applicant',
        'status': 'Under Review'
    }
    
    try:
        # VULNERABILITY: Directly process user-controlled template content with Jinja2
        # This is analogous to templateEngine.process(this.template, ctx) in MailNotifier
        # where the template path/content can be controlled by the attacker
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_content)
        rendered_output = template.render(**preview_data)
    except Exception as e:
        rendered_output = f"Template Error: {str(e)}"
    
    return render_template('template_preview.html',
                          template_name=template_name,
                          template_content=template_content,
                          rendered_output=rendered_output)

# Direct template rendering endpoint - accepts template content directly
# Simulates the scenario where attacker has write access to control template
@app.route('/admin/notify/test', methods=['POST'])
def test_notification():
    # Get custom template from request - simulates controlling the mail template
    custom_template = request.form.get('notification_template', '')
    recipient = request.form.get('recipient', 'test@example.com')
    
    if not custom_template:
        custom_template = notification_templates.get(current_template, DEFAULT_NOTIFICATION_TEMPLATE)
    
    # Context data for the notification
    context = {
        'applicant_name': recipient,
        'status': 'Test Notification',
        'timestamp': '2024-01-15 10:30:00'
    }
    
    try:
        # VULNERABILITY: Process user-controlled template with Jinja2
        # Direct analogy to Thymeleaf's templateEngine.process() in the CVE
        env = Environment(loader=BaseLoader())
        template = env.from_string(custom_template)
        notification_body = template.render(**context)
    except Exception as e:
        notification_body = f"Error rendering notification: {str(e)}"
    
    return render_template('notification_result.html',
                          recipient=recipient,
                          notification_body=notification_body)

if __name__ == '__main__':
    app.run()
