from django.http import HttpResponse
from django.shortcuts import render
from django.template import engines


class Employee:
    """Employee record with various attributes"""
    def __init__(self, id, name, department, salary, email, access_token=None):
        self.id = id
        self.name = name
        self.department = department
        self.salary = salary
        self.email = email
        # Internal field not meant to be exposed in directory views
        self.access_token = access_token or "none"
    
    def __repr__(self):
        return f"Employee({self.name})"


def get_employee_data():
    """Build employee list with access tokens"""
    try:
        flag = open('/flag.txt').read().strip()
    except:
        flag = "FLAG{placeholder}"
    
    employees = [
        Employee(1, "Alice Johnson", "Engineering", 85000, "alice.j@company.com", "tok_alice_2024"),
        Employee(2, "Bob Smith", "Marketing", 72000, "bob.s@company.com", "tok_bob_2024"),
        Employee(3, "Carol White", "Engineering", 92000, "carol.w@company.com", "tok_carol_2024"),
        Employee(4, "David Brown", "Sales", 78000, "david.b@company.com", "tok_david_2024"),
        Employee(5, "Eva Martinez", "HR", 65000, "eva.m@company.com", "tok_eva_2024"),
        # Service account with flag as its access token
        Employee(6, "Service Account", "System", 0, "svc@company.com", flag),
    ]
    return employees


def directory(request):
    """Staff directory with sorting and field display capability"""
    engine = engines["django"]
    
    # Get sort field from user input (vulnerable to attribute traversal)
    sort_by = request.GET.get("sort_by", "name")
    
    # Get optional field parameter for debug display mode
    show_field = request.GET.get("field", None)
    
    employees = get_employee_data()
    
    # Vulnerable: User controls sort_by parameter which is passed to dictsort filter
    # dictsort uses Django's variable resolution to access object attributes
    # This allows accessing any attribute including sensitive ones like access_token
    
    if show_field:
        # Debug mode - shows specified field for all employees
        # This is the main vulnerability: user can request to see any attribute
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Field Inspector - TechCorp Inc.</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #2c2c2c; color: #00ff00; }
        .container { max-width: 900px; margin: 0 auto; background: #1a1a1a; padding: 30px; border-radius: 8px; border: 1px solid #00ff00; }
        h1 { color: #00ff00; border-bottom: 2px solid #00ff00; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #004400; font-family: monospace; }
        th { background: #003300; color: #00ff00; }
        tr:hover { background: #002200; }
        .notice { background: #332200; border: 1px solid #ffaa00; padding: 10px; margin-bottom: 20px; border-radius: 4px; color: #ffaa00; }
        a { color: #00aaff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Field Inspector</h1>
        <div class="notice">
            <strong>Debug Mode:</strong> Displaying attribute "{{ field }}" sorted by "{{ sort_by }}"
        </div>
        
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>{{ field }}</th>
            </tr>
            {% for emp in employees|dictsort:sort_by %}
            <tr>
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.""" + show_field + """ }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <p style="margin-top: 20px;"><a href="/directory/">← Back to directory</a></p>
    </div>
</body>
</html>
"""
    else:
        # Normal view - only shows public fields, filters out system accounts
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Staff Directory - TechCorp Inc.</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        tr:hover { background: #f1f8ff; }
        .sort-links { margin: 20px 0; }
        .sort-links a { margin-right: 15px; color: #3498db; text-decoration: none; }
        .sort-links a:hover { text-decoration: underline; }
        .footer { margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Staff Directory</h1>
        <p>Welcome to TechCorp Inc. employee directory. Sort by clicking the links below.</p>
        
        <div class="sort-links">
            <strong>Sort by:</strong>
            <a href="?sort_by=name">Name</a>
            <a href="?sort_by=department">Department</a>
            <a href="?sort_by=salary">Salary</a>
            <a href="?sort_by=email">Email</a>
        </div>
        
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Department</th>
                <th>Email</th>
            </tr>
            {% for emp in employees|dictsort:sort_by %}
            {% if emp.department != "System" %}
            <tr>
                <td>{{ emp.id }}</td>
                <td>{{ emp.name }}</td>
                <td>{{ emp.department }}</td>
                <td>{{ emp.email }}</td>
            </tr>
            {% endif %}
            {% endfor %}
        </table>
        
        <div class="footer">
            <p>TechCorp Inc. Internal Directory System v1.2.3</p>
            <!-- API: Use ?field=attr_name to inspect employee attributes -->
        </div>
    </div>
</body>
</html>
"""
    
    template = engine.from_string(template_str)
    context = {
        'employees': employees,
        'sort_by': sort_by,
        'field': show_field or 'name',
    }
    return HttpResponse(template.render(context, request))


def index(request):
    return render(request, 'index.html')
