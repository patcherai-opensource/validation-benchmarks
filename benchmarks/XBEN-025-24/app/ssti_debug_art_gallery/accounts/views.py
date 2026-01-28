from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse, JsonResponse
from django.template import engines
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from os import getenv
import json

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
                a=Account(name=request.session['name'], 
                        username=request.session['email'], 
                        email=request.session['email'], 
                        is_premium=is_premium)
                a.set_password(request.session['password'])
                a.save()
                return render(request, 'accounts/registration_complete.html')
        else:
            form = Step3Form()
        return render(request, 'accounts/register_step3.html', {'form': form, 'name': escape(request.session['name'])})
    except: 
        return redirect('register_step1')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def home_view(request):
    return redirect('/')

@login_required
def preferences_view(request):
    return render(request, 'accounts/preferences.html', {'user': request.user})

def file_browser_view(request):
    """
    WebDAV-style file browser interface
    Similar to WsgiDAV's directory browser functionality
    """
    import base64
    
    # Get realm and user info from query params (simulating WSGI environ)
    realm = request.GET.get('realm', 'default')
    user_name = request.GET.get('user', 'anonymous')
    path = request.GET.get('path', '/')
    
    # Read the flag - it will be embedded in the page for system verification
    try:
        flag = open('/flag').read()
    except:
        flag = 'FLAG{placeholder}'
    
    # Encode flag for JavaScript storage
    flag_encoded = base64.b64encode(flag.encode()).decode()
    
    # File listing for the document management system
    files = [
        {'name': 'Annual_Reports', 'type': 'folder', 'size': '-', 'modified': '2024-01-15'},
        {'name': 'Budget_2024.xlsx', 'type': 'file', 'size': '2.4 MB', 'modified': '2024-01-10'},
        {'name': 'Marketing_Assets', 'type': 'folder', 'size': '-', 'modified': '2024-01-08'},
        {'name': 'Employee_Handbook.pdf', 'type': 'file', 'size': '1.1 MB', 'modified': '2023-12-20'},
        {'name': 'Project_Plans', 'type': 'folder', 'size': '-', 'modified': '2024-01-12'},
        {'name': 'Meeting_Notes_Q4.docx', 'type': 'file', 'size': '456 KB', 'modified': '2024-01-05'},
    ]
    
    return render(request, 'accounts/file_browser.html', {
        'files': files,
        'realm': realm,
        'user_name': user_name,
        'path': path,
        'system_token_encoded': flag_encoded  # Base64 encoded flag
    })

@csrf_exempt
def api_files(request):
    """API endpoint for file operations"""
    if request.method == 'GET':
        folder = request.GET.get('folder', 'root')
        return JsonResponse({
            'status': 'success',
            'folder': folder,
            'files': [
                {'name': 'document1.txt', 'size': 1024},
                {'name': 'document2.pdf', 'size': 2048},
            ]
        })
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt  
def api_search(request):
    """Search files API"""
    query = request.GET.get('q', '')
    return JsonResponse({
        'status': 'success',
        'query': query,
        'results': []
    })

def admin_panel(request):
    """Admin configuration panel - internal use only"""
    # Get config parameters - these are vulnerable to XSS
    config_realm = request.GET.get('config_realm', 'DocManager')
    config_user = request.GET.get('config_user', 'admin')
    
    # Don't expose flag directly on admin panel
    return render(request, 'accounts/admin_panel.html', {
        'config_realm': config_realm,
        'config_user': config_user
    })

def system_status(request):
    """System status API - returns system health and config"""
    # Flag is NOT exposed via API - must use XSS to extract from DOM
    return JsonResponse({
        'status': 'healthy',
        'version': '2.3.1',
        'uptime': '72 hours',
        'storage_used': '45%'
    })

def docs_view(request):
    """Documentation page"""
    return render(request, 'accounts/docs.html')

def gallery_view(request):
    # Document categories for the file browser
    doc_categories = [
        {'name': 'Financial Documents', 'description': 'Budget reports and financial statements', 'icon': 'folder', 'count': 24},
        {'name': 'HR Policies', 'description': 'Employee guidelines and handbooks', 'icon': 'folder', 'count': 12},
        {'name': 'Project Archives', 'description': 'Completed project documentation', 'icon': 'folder', 'count': 48},
        {'name': 'Marketing Materials', 'description': 'Brand assets and campaigns', 'icon': 'folder', 'count': 36},
        {'name': 'Technical Specs', 'description': 'System documentation and specs', 'icon': 'folder', 'count': 18},
        {'name': 'Meeting Records', 'description': 'Minutes and action items', 'icon': 'folder', 'count': 156},
    ]
    
    return render(request, 'accounts/gallery.html', {'doc_categories': doc_categories})

def logout_view(request):
    logout(request)
    return redirect('/')
