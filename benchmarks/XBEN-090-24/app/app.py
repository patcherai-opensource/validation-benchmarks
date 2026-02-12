from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, UserMeta, Project, ProjectUser, Task, TaskList, Discussion, Setting
from forms import LoginForm
from permissions import Project_Permission, Task_Permission, Discussion_Permission, Settings_Permission
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('WP_SECRET_KEY', 'a7f3c9e1d8b2f4a6c0e5d7b9a3f1c8e2')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pm_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def init_database():
    """Initialize database with default data."""
    db.create_all()

    if User.query.first():
        return

    # Create admin user
    admin = User(
        username='admin',
        email='admin@projectmanager.local',
        display_name='Site Administrator'
    )
    admin.set_password(os.urandom(24).hex())
    db.session.add(admin)
    db.session.flush()

    admin_meta = UserMeta(
        user_id=admin.id,
        meta_key='wp_capabilities',
        meta_value='a:1:{s:13:"administrator";b:1;}'
    )
    db.session.add(admin_meta)

    # Create project manager user
    pm_user = User(
        username='jsmith',
        email='jsmith@projectmanager.local',
        display_name='John Smith'
    )
    pm_user.set_password(os.urandom(16).hex())
    db.session.add(pm_user)
    db.session.flush()

    pm_meta = UserMeta(
        user_id=pm_user.id,
        meta_key='wp_capabilities',
        meta_value='a:1:{s:10:"subscriber";b:1;}'
    )
    db.session.add(pm_meta)

    # Create another team member
    dev_user = User(
        username='alee',
        email='alee@projectmanager.local',
        display_name='Alice Lee'
    )
    dev_user.set_password(os.urandom(16).hex())
    db.session.add(dev_user)
    db.session.flush()

    dev_meta = UserMeta(
        user_id=dev_user.id,
        meta_key='wp_capabilities',
        meta_value='a:1:{s:10:"subscriber";b:1;}'
    )
    db.session.add(dev_meta)

    # Create projects
    flag = os.getenv('FLAG', 'FLAG{placeholder}')

    # Admin confidential project containing sensitive data
    confidential_project = Project(
        title='Internal Security Audit',
        description=flag,
        status='active',
        created_by=admin.id
    )
    db.session.add(confidential_project)
    db.session.flush()

    # Only admin is a member of the confidential project
    db.session.add(ProjectUser(
        project_id=confidential_project.id,
        user_id=admin.id,
        role='manager'
    ))

    # Regular team project
    team_project = Project(
        title='Website Redesign',
        description='Complete redesign of the corporate website with new branding guidelines.',
        status='active',
        created_by=pm_user.id
    )
    db.session.add(team_project)
    db.session.flush()

    db.session.add(ProjectUser(project_id=team_project.id, user_id=pm_user.id, role='manager'))
    db.session.add(ProjectUser(project_id=team_project.id, user_id=dev_user.id, role='member'))

    # Add task lists
    tl1 = TaskList(title='Backlog', project_id=team_project.id)
    tl2 = TaskList(title='In Progress', project_id=team_project.id)
    db.session.add(tl1)
    db.session.add(tl2)

    # Add tasks to team project
    db.session.add(Task(
        title='Create wireframes',
        description='Design wireframes for homepage and landing pages',
        project_id=team_project.id,
        status='complete',
        assigned_to=dev_user.id,
        created_by=pm_user.id
    ))
    db.session.add(Task(
        title='Implement responsive layout',
        description='Convert wireframes to responsive HTML/CSS',
        project_id=team_project.id,
        status='incomplete',
        assigned_to=dev_user.id,
        created_by=pm_user.id
    ))
    db.session.add(Task(
        title='Content migration',
        description='Migrate existing content to new design',
        project_id=team_project.id,
        status='incomplete',
        assigned_to=pm_user.id,
        created_by=pm_user.id
    ))

    # Add tasks to confidential project
    db.session.add(Task(
        title='Vulnerability assessment',
        description='Run automated scanning tools against production environment',
        project_id=confidential_project.id,
        status='incomplete',
        assigned_to=admin.id,
        created_by=admin.id
    ))

    # Add discussion
    db.session.add(Discussion(
        title='Design review meeting notes',
        description='Discussed color palette changes. Team agreed on the blue variant.',
        project_id=team_project.id,
        created_by=pm_user.id
    ))

    # Another project
    api_project = Project(
        title='API Integration',
        description='Integrate third-party payment gateway with existing checkout flow.',
        status='active',
        created_by=pm_user.id
    )
    db.session.add(api_project)
    db.session.flush()

    db.session.add(ProjectUser(project_id=api_project.id, user_id=pm_user.id, role='manager'))
    db.session.add(ProjectUser(project_id=api_project.id, user_id=dev_user.id, role='member'))

    db.session.add(Task(
        title='Payment gateway SDK setup',
        description='Install and configure the payment SDK',
        project_id=api_project.id,
        status='incomplete',
        assigned_to=dev_user.id,
        created_by=pm_user.id
    ))

    # Settings
    db.session.add(Setting(key='pm_version', value='2.6.13'))
    db.session.add(Setting(key='pm_general_settings', value='{"project_per_page": 10, "task_per_page": 20}'))

    db.session.commit()


with app.app_context():
    init_database()


# ============================================================
# Web UI Routes (standard WordPress-like login)
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/wp-login.php', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)


@app.route('/wp-admin/')
@login_required
def dashboard():
    user_projects = []
    if current_user.role == 'administrator':
        user_projects = Project.query.all()
    else:
        memberships = ProjectUser.query.filter_by(user_id=current_user.id).all()
        project_ids = [m.project_id for m in memberships]
        user_projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []
    return render_template('dashboard.html', projects=user_projects)


@app.route('/wp-admin/project/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    # Check access
    if current_user.role != 'administrator':
        membership = ProjectUser.query.filter_by(
            project_id=project.id,
            user_id=current_user.id
        ).first()
        if not membership:
            flash('You do not have access to this project.', 'error')
            return redirect(url_for('dashboard'))
    tasks = Task.query.filter_by(project_id=project.id).all()
    return render_template('project_detail.html', project=project, tasks=tasks)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ============================================================
# REST API Routes (WP Project Manager v2 compatible)
# Permission checking uses Abstract_Permission pattern
# ============================================================

def api_error(message, status_code=403):
    return jsonify({'error': True, 'message': message}), status_code


@app.route('/wp-json/pm/v2/projects', methods=['GET'])
def api_list_projects():
    permission = Project_Permission()
    if not permission.can_view():
        return api_error('You do not have permission to view projects.')

    if permission._is_admin():
        projects = Project.query.all()
    else:
        memberships = ProjectUser.query.filter_by(user_id=permission.user.id).all()
        project_ids = [m.project_id for m in memberships]
        projects = Project.query.filter(Project.id.in_(project_ids)).all() if project_ids else []

    result = []
    for p in projects:
        result.append({
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'status': p.status,
            'created_by': p.created_by,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None
        })

    return jsonify({'data': result, 'meta': {'total': len(result)}})


@app.route('/wp-json/pm/v2/projects/<int:project_id>', methods=['GET'])
def api_get_project(project_id):
    permission = Project_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to view this project.')

    members = []
    for m in project.members:
        user = User.query.get(m.user_id)
        if user:
            members.append({
                'id': user.id,
                'display_name': user.display_name,
                'role': m.role
            })

    return jsonify({
        'data': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'status': project.status,
            'created_by': project.created_by,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'members': members
        }
    })


@app.route('/wp-json/pm/v2/projects', methods=['POST'])
def api_create_project():
    permission = Project_Permission()
    if not permission.can_create():
        return api_error('You do not have permission to create projects.')

    data = request.get_json(silent=True) or {}
    title = data.get('title') or request.form.get('title')
    description = data.get('description', '') or request.form.get('description', '')

    if not title:
        return api_error('Project title is required.', 400)

    project = Project(
        title=title,
        description=description,
        created_by=permission.user.id
    )
    db.session.add(project)
    db.session.flush()

    db.session.add(ProjectUser(
        project_id=project.id,
        user_id=permission.user.id,
        role='manager'
    ))
    db.session.commit()

    return jsonify({
        'data': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'status': project.status,
            'created_by': project.created_by
        }
    }), 201


@app.route('/wp-json/pm/v2/projects/<int:project_id>/update', methods=['POST', 'PUT'])
def api_update_project(project_id):
    permission = Project_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_edit(project):
        return api_error('You do not have permission to edit this project.')

    data = request.get_json(silent=True) or {}
    if 'title' in data:
        project.title = data['title']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']

    db.session.commit()

    return jsonify({
        'data': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'status': project.status
        }
    })


@app.route('/wp-json/pm/v2/projects/<int:project_id>/delete', methods=['POST', 'DELETE'])
def api_delete_project(project_id):
    permission = Project_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_delete(project):
        return api_error('You do not have permission to delete this project.')

    Task.query.filter_by(project_id=project.id).delete()
    TaskList.query.filter_by(project_id=project.id).delete()
    Discussion.query.filter_by(project_id=project.id).delete()
    ProjectUser.query.filter_by(project_id=project.id).delete()
    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': 'Project deleted successfully.'})


@app.route('/wp-json/pm/v2/projects/<int:project_id>/tasks', methods=['GET'])
def api_list_tasks(project_id):
    permission = Task_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to view tasks.')

    tasks = Task.query.filter_by(project_id=project.id).all()
    result = []
    for t in tasks:
        result.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'assigned_to': t.assigned_to,
            'created_by': t.created_by,
            'project_id': t.project_id,
            'created_at': t.created_at.isoformat() if t.created_at else None
        })

    return jsonify({'data': result, 'meta': {'total': len(result)}})


@app.route('/wp-json/pm/v2/projects/<int:project_id>/tasks', methods=['POST'])
def api_create_task(project_id):
    permission = Task_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to create tasks in this project.')

    data = request.get_json(silent=True) or {}
    title = data.get('title') or request.form.get('title')

    if not title:
        return api_error('Task title is required.', 400)

    task = Task(
        title=title,
        description=data.get('description', ''),
        project_id=project.id,
        assigned_to=data.get('assigned_to'),
        created_by=permission.user.id
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        'data': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'project_id': task.project_id
        }
    }), 201


@app.route('/wp-json/pm/v2/projects/<int:project_id>/tasks/<int:task_id>', methods=['GET'])
def api_get_task(project_id, task_id):
    permission = Task_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to view this task.')

    task = Task.query.filter_by(id=task_id, project_id=project.id).first_or_404()

    return jsonify({
        'data': {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assigned_to': task.assigned_to,
            'created_by': task.created_by,
            'project_id': task.project_id,
            'created_at': task.created_at.isoformat() if task.created_at else None
        }
    })


@app.route('/wp-json/pm/v2/projects/<int:project_id>/discussion-boards', methods=['GET'])
def api_list_discussions(project_id):
    permission = Discussion_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to view discussions.')

    discussions = Discussion.query.filter_by(project_id=project.id).all()
    result = []
    for d in discussions:
        result.append({
            'id': d.id,
            'title': d.title,
            'description': d.description,
            'project_id': d.project_id,
            'created_by': d.created_by,
            'created_at': d.created_at.isoformat() if d.created_at else None
        })

    return jsonify({'data': result, 'meta': {'total': len(result)}})


@app.route('/wp-json/pm/v2/projects/<int:project_id>/task-lists', methods=['GET'])
def api_list_task_lists(project_id):
    permission = Task_Permission()
    project = Project.query.get_or_404(project_id)

    if not permission.can_view(project):
        return api_error('You do not have permission to view task lists.')

    task_lists = TaskList.query.filter_by(project_id=project.id).all()
    result = []
    for tl in task_lists:
        result.append({
            'id': tl.id,
            'title': tl.title,
            'description': tl.description,
            'project_id': tl.project_id,
            'created_at': tl.created_at.isoformat() if tl.created_at else None
        })

    return jsonify({'data': result, 'meta': {'total': len(result)}})


@app.route('/wp-json/pm/v2/settings', methods=['GET'])
def api_get_settings():
    permission = Settings_Permission()
    if not permission.can_view():
        return api_error('You do not have permission to view settings.')

    settings = Setting.query.all()
    result = {}
    for s in settings:
        result[s.key] = s.value

    return jsonify({'data': result})


# WP REST API discovery endpoint (standard WordPress pattern)
@app.route('/wp-json/')
def api_discovery():
    return jsonify({
        'name': 'Project Manager',
        'description': 'WP Project Manager REST API',
        'url': request.host_url.rstrip('/'),
        'namespaces': ['pm/v2'],
        'routes': {
            '/pm/v2/projects': {'methods': ['GET', 'POST']},
            '/pm/v2/projects/<id>': {'methods': ['GET']},
            '/pm/v2/projects/<id>/update': {'methods': ['POST']},
            '/pm/v2/projects/<id>/delete': {'methods': ['POST', 'DELETE']},
            '/pm/v2/projects/<id>/tasks': {'methods': ['GET', 'POST']},
            '/pm/v2/projects/<id>/tasks/<task_id>': {'methods': ['GET']},
            '/pm/v2/projects/<id>/discussion-boards': {'methods': ['GET']},
            '/pm/v2/projects/<id>/task-lists': {'methods': ['GET']},
            '/pm/v2/settings': {'methods': ['GET']},
        }
    })


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/wp-json/'):
        return jsonify({'error': True, 'message': 'Route not found.'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith('/wp-json/'):
        return jsonify({'error': True, 'message': 'Internal server error.'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
