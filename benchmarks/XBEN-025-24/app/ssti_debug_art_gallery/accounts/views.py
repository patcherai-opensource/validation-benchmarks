from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse, JsonResponse
from django.template import engines
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from os import getenv
import re
from datetime import datetime
import json

# Task scheduler configurations with secrets
# In production, these would be stored in database with masking
def get_task_configs():
    try:
        flag = open('/flag').read()
    except:
        flag = 'FLAG{placeholder}'
    
    return {
        'etl_pipeline': {
            'task_id': 'etl_pipeline',
            'name': 'ETL Data Pipeline',
            'schedule': '0 2 * * *',
            'status': 'active',
            'config': {
                'source_db': 'postgres://datauser:***@db.internal:5432/warehouse',
                'target_bucket': 's3://data-lake/processed',
                'api_key': '***MASKED***',
                'secret_token': flag,
            },
            'last_run': '2024-01-15T02:00:00',
            'next_run': '2024-01-16T02:00:00'
        },
        'backup_job': {
            'task_id': 'backup_job', 
            'name': 'Daily Backup',
            'schedule': '0 3 * * *',
            'status': 'active',
            'config': {
                'backup_path': '/var/backups/',
                'retention_days': 30,
                'encryption_key': '***MASKED***'
            },
            'last_run': '2024-01-15T03:00:00',
            'next_run': '2024-01-16T03:00:00'
        },
        'report_generator': {
            'task_id': 'report_generator',
            'name': 'Weekly Reports',
            'schedule': '0 6 * * 1',
            'status': 'paused',
            'config': {
                'output_dir': '/reports/',
                'email_recipients': 'team@example.com',
                'smtp_password': '***MASKED***'
            },
            'last_run': '2024-01-08T06:00:00',
            'next_run': '2024-01-15T06:00:00'
        }
    }

def mask_secrets(config_dict):
    """Mask sensitive values in configuration"""
    masked = {}
    for key, value in config_dict.items():
        if any(s in key.lower() for s in ['secret', 'token', 'password', 'key', 'api']):
            masked[key] = '***MASKED***'
        else:
            masked[key] = value
    return masked

def _lenient_parse_datetime(date_str):
    """
    Parse datetime string leniently - this is the vulnerable function
    Inspired by Airflow's timezone.parse with strict=False
    Attempts to extract a valid datetime from potentially malformed input
    """
    if not date_str:
        return None
    
    # Try common datetime formats, accepting additional suffix characters
    patterns = [
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # ISO format
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # Standard format
        r'^(\d{4}-\d{2}-\d{2})',  # Date only
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                dt_str = match.group(1)
                if 'T' in dt_str:
                    return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                elif ' ' in dt_str:
                    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                else:
                    return datetime.strptime(dt_str, '%Y-%m-%d')
            except:
                continue
    return None

def _check_unmask_bypass(date_str):
    """
    Business logic flaw: if the execution_date contains special suffix,
    the masking is bypassed. This simulates the Airflow vulnerability where
    malformed datetime parameters could expose unmasked secrets.
    """
    if not date_str:
        return False
    # The vulnerability: appending 'raw' or 'unmasked' to the date bypasses masking
    # e.g., 2024-01-15T02:00:00raw or 2024-01-15T02:00:00+unmasked
    lower_str = date_str.lower()
    return 'raw' in lower_str[19:] if len(lower_str) > 19 else False


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
                a = Account(name=request.session['name'], 
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
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def home_view(request):
    return redirect('/')

@login_required
def preferences_view(request):
    return render(request, 'accounts/preferences.html', {'user': request.user})

def dashboard_view(request):
    """Main task scheduler dashboard"""
    tasks = get_task_configs()
    task_list = []
    for task_id, task in tasks.items():
        task_list.append({
            'task_id': task_id,
            'name': task['name'],
            'schedule': task['schedule'],
            'status': task['status'],
            'last_run': task['last_run'],
            'next_run': task['next_run']
        })
    return render(request, 'accounts/dashboard.html', {'tasks': task_list})

def task_detail_view(request):
    """
    View task details including rendered configuration.
    Accepts task_id and execution_date parameters.
    
    The execution_date parameter is parsed leniently for compatibility
    with various date formats from different client systems.
    """
    task_id = request.GET.get('task_id')
    execution_date = request.GET.get('execution_date', '')
    
    tasks = get_task_configs()
    
    if not task_id or task_id not in tasks:
        return JsonResponse({
            'error': 'Task not found',
            'available_tasks': list(tasks.keys())
        }, status=404)
    
    task = tasks[task_id]
    
    # Parse the execution date (lenient parsing for compatibility)
    parsed_date = _lenient_parse_datetime(execution_date)
    
    # Business logic flaw: check if masking should be bypassed
    # This simulates the Airflow CVE where malformed datetime params exposed secrets
    bypass_masking = _check_unmask_bypass(execution_date)
    
    # Prepare config - mask secrets unless bypass condition is met
    if bypass_masking:
        config_display = task['config']
    else:
        config_display = mask_secrets(task['config'])
    
    response_data = {
        'task_id': task['task_id'],
        'name': task['name'],
        'schedule': task['schedule'],
        'status': task['status'],
        'execution_date_requested': execution_date,
        'execution_date_parsed': parsed_date.isoformat() if parsed_date else None,
        'config': config_display,
        'last_run': task['last_run'],
        'next_run': task['next_run']
    }
    
    return JsonResponse(response_data)

def task_logs_view(request):
    """View task execution logs"""
    task_id = request.GET.get('task_id')
    execution_date = request.GET.get('execution_date', '')
    
    tasks = get_task_configs()
    
    if not task_id or task_id not in tasks:
        return JsonResponse({
            'error': 'Task not found',
            'message': 'Use /tasks/detail?task_id=<id>&execution_date=<date> to view task details'
        }, status=404)
    
    # Parse the execution date
    parsed_date = _lenient_parse_datetime(execution_date)
    
    # Sample log data
    logs = [
        {'timestamp': '2024-01-15T02:00:01', 'level': 'INFO', 'message': 'Task started'},
        {'timestamp': '2024-01-15T02:00:05', 'level': 'INFO', 'message': 'Processing data...'},
        {'timestamp': '2024-01-15T02:00:30', 'level': 'INFO', 'message': 'Task completed successfully'},
    ]
    
    return JsonResponse({
        'task_id': task_id,
        'execution_date': parsed_date.isoformat() if parsed_date else execution_date,
        'logs': logs
    })

def logout_view(request):
    logout(request)
    return redirect('/')
