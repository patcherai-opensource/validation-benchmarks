from django.shortcuts import render, redirect
from .forms import Step1Form, Step2Form, Step3Form, LoginForm
from .models import Account
from django.http import HttpResponse, JsonResponse
from django.template import engines
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from os import getenv
import os


class TeamMember:
    """Internal class representing team members with their attributes"""
    def __init__(self, name, department, role, employee_id, join_date, internal_token=None):
        self.name = name
        self.department = department
        self.role = role
        self.employee_id = employee_id
        self.join_date = join_date
        # Internal token used for API access - should never be exposed
        self._internal_token = internal_token or "default-token"
    
    def __repr__(self):
        return f"<TeamMember: {self.name}>"


def get_team_data():
    """Load team member data - includes sensitive internal tokens"""
    # Load the secret flag from environment or file
    flag = os.environ.get('FLAG', '')
    if not flag and os.path.exists('/flag.txt'):
        flag = open('/flag.txt').read().strip()
    
    return [
        TeamMember(
            name="Alice Johnson",
            department="Engineering",
            role="Senior Developer",
            employee_id="EMP001",
            join_date="2019-03-15",
            internal_token=flag  # The flag is stored as Alice's internal token
        ),
        TeamMember(
            name="Bob Smith",
            department="Marketing",
            role="Marketing Manager",
            employee_id="EMP002",
            join_date="2020-06-22",
            internal_token="mk-token-7892"
        ),
        TeamMember(
            name="Carol White",
            department="Engineering",
            role="DevOps Engineer",
            employee_id="EMP003",
            join_date="2021-01-10",
            internal_token="dv-token-3456"
        ),
        TeamMember(
            name="David Brown",
            department="Sales",
            role="Sales Representative",
            employee_id="EMP004",
            join_date="2022-08-05",
            internal_token="sl-token-1234"
        ),
        TeamMember(
            name="Eva Garcia",
            department="HR",
            role="HR Specialist",
            employee_id="EMP005",
            join_date="2018-11-30",
            internal_token="hr-token-5678"
        ),
        TeamMember(
            name="Frank Miller",
            department="Engineering",
            role="Junior Developer",
            employee_id="EMP006",
            join_date="2023-02-14",
            internal_token="en-token-9012"
        ),
    ]


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
    except Exception as e:
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
    """Main dashboard showing company overview"""
    return render(request, 'accounts/dashboard.html')

def team_directory_view(request):
    """
    Team directory view - allows sorting team members by various fields.
    The sort_by parameter is used for sorting and also to display the sort key values.
    
    VULNERABILITY: CVE-2021-45116-like - The sort_by parameter is used with Django's
    Variable resolution mechanism to access object attributes. An attacker can access 
    private attributes like _internal_token by passing it as the sort key.
    """
    from django.template import Variable, VariableDoesNotExist
    
    # Get sort parameter from request - default to 'name'
    sort_by = request.GET.get('sort_by', 'name')
    
    # Basic input validation - allow common sort fields
    # Note: This validation is intentionally incomplete, missing underscore check
    # allowing access to private attributes prefixed with underscore
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._')
    if not all(c in allowed_chars for c in sort_by):
        sort_by = 'name'
    
    team_members = get_team_data()
    
    # Sort the team members by the specified field using Django's Variable resolution
    # This mimics the dictsort filter behavior and allows accessing any attribute
    def get_sort_key(obj):
        try:
            # Use Django's Variable class to resolve the attribute
            # This is the vulnerable pattern from CVE-2021-45116
            var = Variable(sort_by)
            return var.resolve({'item': obj}.get('item', obj).__class__.__dict__.get(sort_by, getattr(obj, sort_by, '')))
        except (VariableDoesNotExist, AttributeError, TypeError):
            try:
                return getattr(obj, sort_by, '')
            except:
                return ''
    
    # Actually just use getattr which is simpler and still vulnerable
    def get_attr_value(obj, attr_name):
        """Get attribute value - vulnerable to accessing private attributes"""
        try:
            return getattr(obj, attr_name, '')
        except:
            return ''
    
    # Sort using the attribute
    try:
        sorted_members = sorted(team_members, key=lambda x: str(get_attr_value(x, sort_by)))
    except:
        sorted_members = team_members
    
    # Add the sort key value to each member for display (this is the vulnerability!)
    # We're exposing whatever attribute the user requested, including private ones
    members_with_sort_values = []
    for member in sorted_members:
        sort_value = get_attr_value(member, sort_by)
        members_with_sort_values.append({
            'member': member,
            'sort_value': sort_value
        })
    
    return render(request, 'accounts/team_directory.html', {
        'team_members': members_with_sort_values,
        'sort_by': sort_by,
        'current_sort': sort_by,
    })


def api_departments_view(request):
    """API endpoint to list departments"""
    departments = [
        {"id": 1, "name": "Engineering", "head": "CTO", "budget": 500000},
        {"id": 2, "name": "Marketing", "head": "CMO", "budget": 200000},
        {"id": 3, "name": "Sales", "head": "VP Sales", "budget": 300000},
        {"id": 4, "name": "HR", "head": "HR Director", "budget": 150000},
    ]
    return JsonResponse({"departments": departments})


def api_projects_view(request):
    """API endpoint to list projects"""
    projects = [
        {"id": 1, "name": "Project Alpha", "status": "active", "team_size": 5},
        {"id": 2, "name": "Project Beta", "status": "planning", "team_size": 3},
        {"id": 3, "name": "Project Gamma", "status": "completed", "team_size": 8},
    ]
    return JsonResponse({"projects": projects})


def reports_view(request):
    """Reports page - placeholder for future functionality"""
    return render(request, 'accounts/reports.html')


def logout_view(request):
    logout(request)
    return redirect('/')
