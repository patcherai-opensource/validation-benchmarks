from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import Template, Context, engines
from django.utils.safestring import mark_safe
import json


class Employee:
    """Employee data class for HR system"""
    def __init__(self, id, name, department, salary, hire_date, _internal_token=None):
        self.id = id
        self.name = name
        self.department = department
        self.salary = salary
        self.hire_date = hire_date
        # Internal system token - should never be exposed
        self._internal_token = _internal_token
    
    def __repr__(self):
        return f"Employee({self.id}, {self.name})"


def get_flag():
    """Read flag from secure location"""
    try:
        return open('/flag.txt').read().strip()
    except:
        return "FLAG{placeholder}"


# Sample employee data for the HR portal
def get_employees():
    flag = get_flag()
    return [
        Employee(1, "Alice Johnson", "Engineering", 95000, "2020-03-15", _internal_token=flag),
        Employee(2, "Bob Smith", "Marketing", 72000, "2019-08-22", _internal_token=flag),
        Employee(3, "Carol Williams", "Engineering", 105000, "2018-01-10", _internal_token=flag),
        Employee(4, "David Brown", "Sales", 68000, "2021-06-01", _internal_token=flag),
        Employee(5, "Eve Davis", "HR", 78000, "2017-11-30", _internal_token=flag),
    ]


def index(request):
    """Homepage - Employee Directory"""
    return render(request, 'index.html')


def employees(request):
    """Employee listing with sorting capability"""
    sort_by = request.GET.get('sort_by', 'name')
    
    employees_list = get_employees()
    
    # Template with user-controlled sort parameter passed to dictsort
    engine = engines["django"]
    
    # The vulnerability: user input (sort_key) is used with a custom filter
    # that mimics Django's Variable resolution vulnerability (CVE-2021-45116).
    # This allows accessing any attribute including private ones (underscore-prefixed).
    template_str = '''{% load hr_extras %}
    <!DOCTYPE html>
    <html>
    <head>
        <title>Employee Directory - TechCorp HR Portal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; word-break: break-all; }
            th { background: #3498db; color: white; }
            tr:hover { background: #f1f1f1; }
            .sort-links { margin: 20px 0; }
            .sort-links a { margin-right: 15px; color: #3498db; text-decoration: none; }
            .sort-links a:hover { text-decoration: underline; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 20px; color: #666; text-decoration: none; }
            .current-sort { color: #666; font-size: 14px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/employees/">Employees</a>
                <a href="/departments/">Departments</a>
                <a href="/reports/">Reports</a>
            </div>
            <h1>Employee Directory</h1>
            <div class="sort-links">
                Sort by: 
                <a href="?sort_by=name">Name</a>
                <a href="?sort_by=department">Department</a>
                <a href="?sort_by=salary">Salary</a>
                <a href="?sort_by=hire_date">Hire Date</a>
            </div>
            <p class="current-sort">Sorted by: {{ sort_key }}</p>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Department</th>
                    <th>Salary</th>
                    <th>Hire Date</th>
                    <th>{{ sort_key|title }}</th>
                </tr>
                {% for emp in employees|dictsort:sort_key %}
                <tr>
                    <td>{{ emp.id }}</td>
                    <td>{{ emp.name }}</td>
                    <td>{{ emp.department }}</td>
                    <td>${{ emp.salary|floatformat:0 }}</td>
                    <td>{{ emp.hire_date }}</td>
                    <td>{{ emp|get_attr:sort_key }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    '''
    
    template = engine.from_string(template_str)
    context = {
        'employees': employees_list,
        'sort_key': sort_by,
    }
    
    return HttpResponse(template.render(context, request))


def departments(request):
    """Department overview page"""
    return render(request, 'departments.html')


def reports(request):
    """Reports page"""
    return render(request, 'reports.html')


def api_employees(request):
    """API endpoint for employee data (limited info)"""
    employees_list = get_employees()
    data = [
        {
            'id': emp.id,
            'name': emp.name,
            'department': emp.department
        }
        for emp in employees_list
    ]
    return JsonResponse({'employees': data, 'count': len(data)})


def health(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'techcorp-hr-portal'})
