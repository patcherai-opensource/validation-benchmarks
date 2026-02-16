import os
import functools
from flask import Flask, render_template, redirect, url_for, request, jsonify, g, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Project, Task, Milestone, TaskList, ProjectMember, Setting
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
db.init_app(app)


def read_flag():
    try:
        with open('/app/data/system_config.dat', 'r') as f:
            return f.read().strip()
    except Exception:
        return 'flag{placeholder}'


def get_api_version():
    return 'v2'


def resolve_request_identity():
    """Resolve the effective user for the current API request."""
    member_id = request.values.get('member_id')
    if not member_id:
        json_data = request.get_json(silent=True)
        if json_data and isinstance(json_data, dict):
            member_id = json_data.get('member_id')
    if member_id:
        try:
            member_id = int(member_id)
        except (ValueError, TypeError):
            member_id = 0
    else:
        member_id = 0

    if member_id == 0 and 'uid' in session:
        member_id = session['uid']

    if member_id:
        user = db.session.get(User, member_id)
        if user:
            g.current_user = user
            return
    g.current_user = None


@app.before_request
def before_request_handler():
    resolve_request_identity()


def require_authenticated(f):
    """Require a resolved user identity for this endpoint."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            return jsonify({'error': 'Authentication required.'}), 401
        return f(*args, **kwargs)
    return wrapper


def require_manager(f):
    """Require manager or admin role."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            return jsonify({'error': 'Authentication required.'}), 401
        if g.current_user.role not in ('admin', 'manager'):
            return jsonify({'error': 'You do not have permission to perform this action.'}), 403
        return f(*args, **kwargs)
    return wrapper


def require_project_access(f):
    """Check the user has access to the requested project."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            return jsonify({'error': 'Authentication required.'}), 401
        project_id = kwargs.get('project_id') or request.values.get('project_id')
        if project_id:
            membership = ProjectMember.query.filter_by(
                project_id=int(project_id), user_id=g.current_user.id
            ).first()
            if not membership and g.current_user.role not in ('admin', 'manager'):
                return jsonify({'error': 'You do not have access to this project.'}), 403
        return f(*args, **kwargs)
    return wrapper


def seed_database():
    db.create_all()

    if User.query.first() is not None:
        return

    admin = User(username='admin', email='admin@taskflow.local', role='admin')
    admin.password_hash = generate_password_hash('Xt!9kL#mPz2wQv')
    db.session.add(admin)

    manager = User(username='manager', email='manager@taskflow.local', role='manager')
    manager.password_hash = generate_password_hash('Rj7$nBhYc4dW')
    db.session.add(manager)

    member = User(username='developer', email='dev@taskflow.local', role='member')
    member.password_hash = generate_password_hash('devpass123')
    db.session.add(member)

    db.session.flush()

    # Create projects
    proj_internal = Project(
        title='Internal Platform',
        description='Core platform development and maintenance',
        status='active',
        created_by=admin.id,
    )
    db.session.add(proj_internal)

    proj_client = Project(
        title='Client Portal',
        description='Customer-facing portal application',
        status='active',
        created_by=manager.id,
    )
    db.session.add(proj_client)

    db.session.flush()

    # Project memberships
    db.session.add(ProjectMember(project_id=proj_internal.id, user_id=admin.id, role='admin'))
    db.session.add(ProjectMember(project_id=proj_internal.id, user_id=manager.id, role='manager'))
    db.session.add(ProjectMember(project_id=proj_internal.id, user_id=member.id, role='member'))
    db.session.add(ProjectMember(project_id=proj_client.id, user_id=admin.id, role='admin'))
    db.session.add(ProjectMember(project_id=proj_client.id, user_id=manager.id, role='manager'))

    db.session.flush()

    # Task lists
    tl_backlog = TaskList(title='Backlog', project_id=proj_internal.id, order=0)
    tl_progress = TaskList(title='In Progress', project_id=proj_internal.id, order=1)
    tl_done = TaskList(title='Done', project_id=proj_internal.id, order=2)
    db.session.add_all([tl_backlog, tl_progress, tl_done])
    db.session.flush()

    # Tasks
    db.session.add(Task(
        title='Set up CI/CD pipeline',
        description='Configure automated build and deploy',
        status='complete',
        project_id=proj_internal.id,
        task_list_id=tl_done.id,
        assigned_to=member.id,
        created_by=manager.id,
    ))
    db.session.add(Task(
        title='Database migration tooling',
        description='Implement schema migration scripts',
        status='open',
        project_id=proj_internal.id,
        task_list_id=tl_progress.id,
        assigned_to=member.id,
        created_by=manager.id,
    ))
    db.session.add(Task(
        title='Security audit',
        description='Perform full security audit of REST API',
        status='open',
        project_id=proj_internal.id,
        task_list_id=tl_backlog.id,
        assigned_to=admin.id,
        created_by=admin.id,
    ))

    # Milestones
    db.session.add(Milestone(
        title='v1.0 Release',
        description='First production release',
        status='open',
        project_id=proj_internal.id,
        due_date=datetime(2025, 3, 1),
    ))
    db.session.add(Milestone(
        title='v1.1 Patch',
        description='Bug fix release',
        status='open',
        project_id=proj_internal.id,
        due_date=datetime(2025, 6, 1),
    ))

    # System configuration
    flag_value = read_flag()
    db.session.add(Setting(
        key='system_api_token',
        value=flag_value,
        project_id=None,
        is_global=True,
    ))
    db.session.add(Setting(
        key='notifications_enabled',
        value='true',
        project_id=None,
        is_global=True,
    ))
    db.session.add(Setting(
        key='max_file_upload_mb',
        value='25',
        project_id=None,
        is_global=True,
    ))
    db.session.add(Setting(
        key='default_task_status',
        value='open',
        project_id=proj_internal.id,
        is_global=False,
    ))

    db.session.commit()


with app.app_context():
    seed_database()


@app.route('/')
def index():
    if g.current_user:
        return redirect(url_for('dashboard_page'))
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['uid'] = user.id
            return redirect(url_for('dashboard_page'))
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout_page():
    session.pop('uid', None)
    return redirect(url_for('login_page'))


@app.route('/dashboard')
def dashboard_page():
    if g.current_user is None:
        return redirect(url_for('login_page'))
    projects = Project.query.all()
    return render_template('dashboard.html', user=g.current_user, projects=projects)


@app.route('/ping')
def healthcheck():
    return 'ok', 200


api_prefix = f'/api/{get_api_version()}'


@app.route(f'{api_prefix}/', methods=['GET'])
@app.route(f'{api_prefix}', methods=['GET'])
def api_index():
    return jsonify({
        'name': 'TaskFlow PM API',
        'version': get_api_version(),
        'endpoints': {
            'projects': f'{api_prefix}/projects',
            'tasks': f'{api_prefix}/projects/{{project_id}}/tasks',
            'task_lists': f'{api_prefix}/projects/{{project_id}}/task-lists',
            'milestones': f'{api_prefix}/projects/{{project_id}}/milestones',
            'members': f'{api_prefix}/members',
            'current_member': f'{api_prefix}/current-member',
            'activities': f'{api_prefix}/projects/{{project_id}}/activities',
            'settings': f'{api_prefix}/settings',
            'project_settings': f'{api_prefix}/projects/{{project_id}}/settings',
        },
    })


# --- Projects ---

@app.route(f'{api_prefix}/projects', methods=['GET'])
@require_authenticated
def api_list_projects():
    if g.current_user.role in ('admin', 'manager'):
        projects = Project.query.all()
    else:
        member_projects = ProjectMember.query.filter_by(user_id=g.current_user.id).all()
        project_ids = [m.project_id for m in member_projects]
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
    return jsonify({'data': [p.to_dict() for p in projects]})


@app.route(f'{api_prefix}/projects/<int:project_id>', methods=['GET'])
@require_authenticated
@require_project_access
def api_get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify({'data': project.to_dict()})


@app.route(f'{api_prefix}/projects', methods=['POST'])
@require_manager
def api_create_project():
    data = request.get_json(silent=True) or {}
    project = Project(
        title=data.get('title', 'Untitled'),
        description=data.get('description', ''),
        status='active',
        created_by=g.current_user.id,
    )
    db.session.add(project)
    db.session.flush()
    db.session.add(ProjectMember(
        project_id=project.id, user_id=g.current_user.id, role='admin'
    ))
    db.session.commit()
    return jsonify({'data': project.to_dict()}), 201


@app.route(f'{api_prefix}/projects/<int:project_id>/update', methods=['POST'])
@require_manager
@require_project_access
def api_update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        project.title = data['title']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    db.session.commit()
    return jsonify({'data': project.to_dict()})


@app.route(f'{api_prefix}/projects/<int:project_id>/delete', methods=['POST'])
@require_manager
@require_project_access
def api_delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Project deleted.'})


# --- Tasks ---

@app.route(f'{api_prefix}/projects/<int:project_id>/tasks', methods=['GET'])
@require_authenticated
@require_project_access
def api_list_tasks(project_id):
    tasks = Task.query.filter_by(project_id=project_id).all()
    return jsonify({'data': [t.to_dict() for t in tasks]})


@app.route(f'{api_prefix}/projects/<int:project_id>/tasks/<int:task_id>', methods=['GET'])
@require_authenticated
@require_project_access
def api_get_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    return jsonify({'data': task.to_dict()})


@app.route(f'{api_prefix}/projects/<int:project_id>/tasks', methods=['POST'])
@require_authenticated
@require_project_access
def api_create_task(project_id):
    data = request.get_json(silent=True) or {}
    task = Task(
        title=data.get('title', 'Untitled Task'),
        description=data.get('description', ''),
        status='open',
        project_id=project_id,
        task_list_id=data.get('task_list_id'),
        assigned_to=data.get('assigned_to'),
        created_by=g.current_user.id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'data': task.to_dict()}), 201


@app.route(f'{api_prefix}/projects/<int:project_id>/tasks/<int:task_id>/update', methods=['POST'])
@require_authenticated
@require_project_access
def api_update_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    data = request.get_json(silent=True) or {}
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'assigned_to' in data:
        task.assigned_to = data['assigned_to']
    db.session.commit()
    return jsonify({'data': task.to_dict()})


@app.route(f'{api_prefix}/projects/<int:project_id>/tasks/<int:task_id>/delete', methods=['POST'])
@require_authenticated
@require_project_access
def api_delete_task(project_id, task_id):
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted.'})


# --- Task Lists ---

@app.route(f'{api_prefix}/projects/<int:project_id>/task-lists', methods=['GET'])
@require_authenticated
@require_project_access
def api_list_task_lists(project_id):
    lists = TaskList.query.filter_by(project_id=project_id).order_by(TaskList.order).all()
    return jsonify({'data': [tl.to_dict() for tl in lists]})


# --- Milestones ---

@app.route(f'{api_prefix}/projects/<int:project_id>/milestones', methods=['GET'])
@require_authenticated
@require_project_access
def api_list_milestones(project_id):
    milestones = Milestone.query.filter_by(project_id=project_id).all()
    return jsonify({'data': [m.to_dict() for m in milestones]})


@app.route(f'{api_prefix}/projects/<int:project_id>/milestones', methods=['POST'])
@require_manager
@require_project_access
def api_create_milestone(project_id):
    data = request.get_json(silent=True) or {}
    ms = Milestone(
        title=data.get('title', 'Untitled Milestone'),
        description=data.get('description', ''),
        status='open',
        project_id=project_id,
        due_date=None,
    )
    db.session.add(ms)
    db.session.commit()
    return jsonify({'data': ms.to_dict()}), 201


# --- Users ---

@app.route(f'{api_prefix}/members', methods=['GET'])
@require_authenticated
def api_list_members():
    users = User.query.all()
    return jsonify({'data': [u.to_dict() for u in users]})


@app.route(f'{api_prefix}/members/<int:user_id>', methods=['GET'])
@require_authenticated
def api_get_member(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'data': user.to_dict()})


@app.route(f'{api_prefix}/current-member', methods=['GET'])
@require_authenticated
def api_current_member():
    return jsonify({'data': g.current_user.to_dict()})


# --- Activities ---

@app.route(f'{api_prefix}/projects/<int:project_id>/activities', methods=['GET'])
@require_authenticated
@require_project_access
def api_list_activities(project_id):
    # Simplified activity feed
    tasks = Task.query.filter_by(project_id=project_id).order_by(Task.created_at.desc()).limit(10).all()
    activities = []
    for t in tasks:
        activities.append({
            'type': 'task_created',
            'description': f'Task "{t.title}" created',
            'timestamp': t.created_at.isoformat() if t.created_at else None,
        })
    return jsonify({'data': activities})


# --- Settings (admin-only) ---

@app.route(f'{api_prefix}/settings', methods=['GET'])
@require_manager
def api_get_settings():
    settings = Setting.query.filter_by(is_global=True).all()
    return jsonify({'data': [s.to_dict() for s in settings]})


@app.route(f'{api_prefix}/settings', methods=['POST'])
@require_manager
def api_update_settings():
    data = request.get_json(silent=True) or {}
    key = data.get('key')
    value = data.get('value')
    if not key:
        return jsonify({'error': 'Key is required.'}), 400
    setting = Setting.query.filter_by(key=key, is_global=True).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value, is_global=True)
        db.session.add(setting)
    db.session.commit()
    return jsonify({'data': setting.to_dict()})


@app.route(f'{api_prefix}/projects/<int:project_id>/settings', methods=['GET'])
@require_authenticated
@require_project_access
def api_get_project_settings(project_id):
    settings = Setting.query.filter_by(project_id=project_id, is_global=False).all()
    return jsonify({'data': [s.to_dict() for s in settings]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
