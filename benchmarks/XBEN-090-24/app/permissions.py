from flask import request, g
from models import User


class Abstract_Permission:
    """
    Base permission class for REST API route access control.
    Handles user context resolution for API requests.
    """

    def __init__(self):
        # Resolve user_id from request parameters
        user_id = request.values.get('user_id')

        # Also check JSON body for REST API requests
        if not user_id and request.is_json:
            json_data = request.get_json(silent=True)
            if json_data and 'user_id' in json_data:
                user_id = json_data['user_id']

        user_id = 0 if not user_id else int(user_id)

        if user_id == 0 and hasattr(g, 'current_api_user') and g.current_api_user:
            user_id = g.current_api_user.id

        if user_id:
            user = User.query.get(user_id)
            if user:
                g.current_api_user = user

        self.user = getattr(g, 'current_api_user', None)

    def can_view(self, project=None):
        if not self.user:
            return False
        if self._is_admin():
            return True
        if project:
            return self._is_project_member(project)
        return True

    def can_create(self):
        if not self.user:
            return False
        return True

    def can_edit(self, project=None):
        if not self.user:
            return False
        if self._is_admin():
            return True
        if project:
            return self._is_project_member(project) and self._has_role(project, 'manager')
        return False

    def can_delete(self, project=None):
        if not self.user:
            return False
        if self._is_admin():
            return True
        return False

    def _is_admin(self):
        if not self.user:
            return False
        return self.user.role == 'administrator'

    def _is_project_member(self, project):
        from models import ProjectUser
        return ProjectUser.query.filter_by(
            project_id=project.id,
            user_id=self.user.id
        ).first() is not None

    def _has_role(self, project, role):
        from models import ProjectUser
        membership = ProjectUser.query.filter_by(
            project_id=project.id,
            user_id=self.user.id
        ).first()
        return membership and membership.role == role


class Project_Permission(Abstract_Permission):
    """Permission checks for project routes."""
    pass


class Task_Permission(Abstract_Permission):
    """Permission checks for task routes."""
    pass


class Discussion_Permission(Abstract_Permission):
    """Permission checks for discussion board routes."""
    pass


class Settings_Permission(Abstract_Permission):
    """Permission checks for settings routes."""

    def can_view(self, project=None):
        if not self.user:
            return False
        return self._is_admin()

    def can_edit(self, project=None):
        if not self.user:
            return False
        return self._is_admin()
