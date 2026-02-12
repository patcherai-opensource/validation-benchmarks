from models import UserGroup, User


def get_user_groups(user):
    """Return groups visible to the user based on their role."""
    if user.role in ("admin", "curator"):
        return list(UserGroup.objects(is_active=True))

    user_id = str(user.id)
    return list(UserGroup.objects(
        is_active=True,
        __raw__={"$or": [
            {"user_ids": user_id},
            {"curator_ids": user_id}
        ]}
    ))


def get_user_group_by_id(group_id):
    return UserGroup.objects(id=group_id, is_active=True).first()


def update_user_group(group_id, update_data, requesting_user):
    """Update a user group's membership, connectors, and metadata."""
    group = get_user_group_by_id(group_id)
    if not group:
        return None

    if "user_ids" in update_data:
        validated_user_ids = []
        for uid in update_data["user_ids"]:
            u = User.objects(id=uid).first()
            if u:
                validated_user_ids.append(str(u.id))
        group.user_ids = validated_user_ids

    if "cc_pair_ids" in update_data:
        group.cc_pair_ids = update_data["cc_pair_ids"]

    if "name" in update_data:
        group.name = update_data["name"]

    if "description" in update_data:
        group.description = update_data["description"]

    group.save()
    return group


def create_user_group(name, description="", user_ids=None, curator_ids=None, cc_pair_ids=None):
    group = UserGroup(
        name=name,
        description=description,
        user_ids=user_ids or [],
        curator_ids=curator_ids or [],
        cc_pair_ids=cc_pair_ids or [],
    )
    group.save()
    return group
