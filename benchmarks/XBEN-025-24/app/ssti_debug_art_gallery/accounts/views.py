from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse
from django.template import engines
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.utils.html import escape
from os import getenv
import os

# Simulated file system for directory browser
FILE_SYSTEM = {
    '/': {
        'type': 'directory',
        'children': ['documents', 'images', 'shared', 'system']
    },
    '/documents': {
        'type': 'directory', 
        'children': ['report.pdf', 'notes.txt', 'budget.xlsx']
    },
    '/images': {
        'type': 'directory',
        'children': ['photo1.jpg', 'photo2.png', 'logo.svg']
    },
    '/shared': {
        'type': 'directory',
        'children': ['project_files', 'team_docs']
    },
    '/system': {
        'type': 'directory',
        'children': ['config.ini', 'logs']
    }
}

def register_step1(request):
    if request.method == 'POST':
        form = Step1Form(request.POST)
        if form.is_valid():
            request.session['name'] = form.cleaned_data['name']
            request.session['password'] = form.cleaned_data['password']

            return redirect('register_step2')
    else:
        form = Step1Form()
    return render(request, 'accounts/register_step1.html', {'form': form})

def register_step2(request):
    if 'name' not in request.session:
        return redirect('register_step1')
    
    if request.method == 'POST':
        form = Step2Form(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            return redirect('register_step3')
    else:
        form = Step2Form()
    return render(request, 'accounts/register_step2.html', {'form': form})

def register_step3(request):
    if 'name' not in request.session or 'email' not in request.session:
        return redirect('register_step1')
    try:
        if request.method == 'POST':
            form = Step3Form(request.POST)
            if form.is_valid():
                is_premium = form.cleaned_data['is_premium']
                # Save data or create a user here
                a=Account(name=request.session['name'], 
                        username=request.session['email'], 
                        email=request.session['email'], 
                        is_premium=is_premium)
                a.set_password(request.session['password'])
                a.save()
                return render(request, 'accounts/registration_complete.html')
        else:
            form = Step3Form()
    except: 
        return redirect('register_step1')    
    return render(request, 'accounts/register_step3.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('browser')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def home_view(request):
    return redirect('/')

@login_required
def preferences_view(request):
    return render(request, 'accounts/preferences.html', {'user': request.user})

def browser_view(request):
    """
    Directory browser view - mimics WsgiDAV directory browsing functionality.
    The username and realm are rendered directly without escaping (XSS vulnerability).
    
    To exploit: inject script tags in the 'realm' parameter to execute JavaScript
    that calls document.write(getAdminToken()) to reveal the flag.
    """
    # Get path from query parameter
    path = request.GET.get('path', '/')
    
    # Get realm from query parameter (simulating WsgiDAV realm configuration)
    realm = request.GET.get('realm', 'FileDock WebDAV')
    
    # Get user info
    if request.user.is_authenticated:
        user_name = request.user.name
        access_level = "read-write"
    else:
        user_name = "anonymous"
        access_level = "read-only"
    
    # Get directory listing
    dir_info = FILE_SYSTEM.get(path, FILE_SYSTEM['/'])
    files = []
    if dir_info['type'] == 'directory':
        for child in dir_info['children']:
            child_path = f"{path}/{child}" if path != '/' else f"/{child}"
            child_info = FILE_SYSTEM.get(child_path, {'type': 'file'})
            files.append({
                'name': child,
                'type': child_info.get('type', 'file'),
                'path': child_path,
                'size': '4.0 KB' if child_info.get('type') != 'directory' else '-',
                'modified': '2024-01-15 10:30:00'
            })
    
    # Read flag
    try:
        flag = open('/flag').read()
    except:
        flag = "FLAG{placeholder}"
    
    # Check if XSS payload is attempting to access the admin token
    # The flag is revealed when the attacker successfully injects script that accesses it
    # This simulates how XSS would work in a real browser context
    xss_detected = False
    reveal_flag = False
    
    # Check for common XSS patterns in user-controlled inputs
    xss_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', 'onmouseover=']
    for pattern in xss_patterns:
        if pattern.lower() in realm.lower() or pattern.lower() in user_name.lower():
            xss_detected = True
            # If the XSS payload tries to access the token, reveal the flag
            if 'getadmintoken' in realm.lower() or 'admintoken' in realm.lower() or '_wdav' in realm.lower():
                reveal_flag = True
            if 'getadmintoken' in user_name.lower() or 'admintoken' in user_name.lower() or '_wdav' in user_name.lower():
                reveal_flag = True
            break
    
    # Build the response HTML manually (simulating Jinja2 without autoescape)
    # This is the XSS vulnerability - user_name and realm are not escaped
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FileDock - Directory Browser</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .file-icon {{ margin-right: 10px; }}
        .directory {{ color: #007bff; }}
        .file {{ color: #6c757d; }}
        .auth-info {{ background: #f8f9fa; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
        .breadcrumb {{ background: #e9ecef; }}
        table {{ width: 100%; }}
        th, td {{ padding: 8px 12px; text-align: left; }}
        th {{ background: #343a40; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        tr:hover {{ background: #e0e0e0; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <a class="navbar-brand" href="/browse/">FileDock WebDAV</a>
        <span class="navbar-text">
            Secure File Management
        </span>
    </nav>
    
    <div class="container mt-4">
        <!-- Authentication info section - XSS vulnerability here -->
        <!-- User input (user_name, realm) rendered without escaping -->
        <div class="auth-info">
            <strong>Session Info:</strong> 
            Authenticated user: "{user_name}", 
            realm: "{realm}", 
            access: {access_level}.
        </div>
        
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/browse/?path=/">Root</a></li>
                {"".join([f'<li class="breadcrumb-item"><a href="/browse/?path={p}">{p.split("/")[-1] or "/"}</a></li>' for p in path.split("/") if p])}
            </ol>
        </nav>
        
        <h4>Directory: {escape(path)}</h4>
        
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Modified</th>
                </tr>
            </thead>
            <tbody>
'''
    
    for f in files:
        icon = "📁" if f['type'] == 'directory' else "📄"
        type_class = "directory" if f['type'] == 'directory' else "file"
        if f['type'] == 'directory':
            link = f'<a href="/browse/?path={escape(f["path"])}" class="{type_class}">{icon} {escape(f["name"])}</a>'
        else:
            link = f'<span class="{type_class}">{icon} {escape(f["name"])}</span>'
        
        html += f'''                <tr>
                    <td>{link}</td>
                    <td>{escape(f['type'])}</td>
                    <td>{escape(f['size'])}</td>
                    <td>{escape(f['modified'])}</td>
                </tr>
'''
    
    # If XSS with token access detected, include the flag in the response
    if reveal_flag:
        token_script = f'''
    <script>
        // Admin token accessed via XSS - security breach detected
        var _admin_token = "{flag}";
        document.write("<div style='background:red;color:white;padding:20px;'>SECURITY ALERT: Admin token exposed: " + _admin_token + "</div>");
    </script>'''
    else:
        token_script = '''
    <script>
        // Internal admin token for WebDAV operations
        // Access via getAdminToken() function
        var _wdav_admin_token = "RESTRICTED";
        function getAdminToken() { return _wdav_admin_token; }
    </script>'''
    
    html += f'''            </tbody>
        </table>
        
        <div class="mt-4">
            <small class="text-muted">
                FileDock WebDAV Server v3.2.1 | 
                <a href="/accounts/login/">Login</a> | 
                <a href="/accounts/register/step1/">Register</a>
            </small>
        </div>
        
        <!-- Debug: realm parameter can be customized via ?realm=YourRealm -->
        <!-- TODO: Remove before production - exposes internal token via getAdminToken() -->
    </div>
    
    <script src="/static/js/jquery-3.5.1.slim.min.js"></script>
    <script src="/static/js/bootstrap.min.js"></script>
    {token_script}
</body>
</html>'''
    
    return HttpResponse(html)

def gallery_view(request):
    """Redirect old gallery to new browser interface"""
    return redirect('browser')

def logout_view(request):
    logout(request)
    return redirect('/')
