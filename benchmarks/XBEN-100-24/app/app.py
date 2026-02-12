import os
from flask import Flask, jsonify, request, render_template, g
import database
from models import User, UserGroup, ConnectorCredentialPair, Document_
from auth import (
    create_access_token,
    require_auth,
    require_admin,
    require_curator_or_admin,
    get_current_user,
)
from user_group import (
    get_user_groups,
    get_user_group_by_id,
    update_user_group,
    create_user_group,
)

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = False


@app.errorhandler(404)
def not_found(e):
    return jsonify({"detail": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"detail": "Internal server error"}), 500


# ---- Health / root ----

@app.route("/")
def root():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ---- Auth endpoints ----

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"detail": "Invalid request body"}), 400

    email = data.get("email", "")
    password = data.get("password", "")

    user = User.objects(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({"detail": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"detail": "Account disabled"}), 403

    token = create_access_token(str(user.id), user.role)
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    })


@app.route("/api/auth/me", methods=["GET"])
@require_auth
def get_me():
    return jsonify(g.current_user.to_dict())


# ---- User management (admin only) ----

@app.route("/api/manage/admin/users", methods=["GET"])
@require_admin
def list_users():
    users = User.objects(is_active=True)
    return jsonify([u.to_dict() for u in users])


# ---- User Group management ----

@app.route("/api/manage/admin/user-group", methods=["GET"])
@require_auth
def list_user_groups():
    groups = get_user_groups(g.current_user)
    return jsonify([grp.to_dict() for grp in groups])


@app.route("/api/manage/admin/user-group/<group_id>", methods=["GET"])
@require_auth
def get_user_group(group_id):
    group = get_user_group_by_id(group_id)
    if not group:
        return jsonify({"detail": "Group not found"}), 404

    user_id = str(g.current_user.id)
    if g.current_user.role == "admin":
        return jsonify(group.to_dict())
    if user_id in group.user_ids or user_id in group.curator_ids:
        return jsonify(group.to_dict())

    return jsonify({"detail": "Access denied"}), 403


@app.route("/api/manage/admin/user-group", methods=["POST"])
@require_admin
def create_group():
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"detail": "Name is required"}), 400

    group = create_user_group(
        name=data["name"],
        description=data.get("description", ""),
        user_ids=data.get("user_ids", []),
        curator_ids=data.get("curator_ids", []),
        cc_pair_ids=data.get("cc_pair_ids", []),
    )
    return jsonify(group.to_dict()), 201


@app.route("/api/manage/admin/user-group/<group_id>", methods=["PATCH"])
@require_curator_or_admin
def patch_user_group(group_id):
    """Update user group membership and settings.

    Accessible to curators and admins. The require_curator_or_admin decorator
    validates the user holds a curator or admin role.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"detail": "Invalid request body"}), 400

    updated = update_user_group(group_id, data, g.current_user)
    if not updated:
        return jsonify({"detail": "Group not found"}), 404

    return jsonify(updated.to_dict())


@app.route("/api/manage/admin/user-group/<group_id>", methods=["DELETE"])
@require_admin
def delete_user_group(group_id):
    group = get_user_group_by_id(group_id)
    if not group:
        return jsonify({"detail": "Group not found"}), 404

    group.is_active = False
    group.save()
    return jsonify({"detail": "Group deleted"}), 200


# ---- Connector credential pairs ----

@app.route("/api/manage/connector", methods=["GET"])
@require_auth
def list_connectors():
    pairs = ConnectorCredentialPair.objects()
    return jsonify([p.to_dict() for p in pairs])


# ---- Document search / retrieval ----

@app.route("/api/manage/documents", methods=["GET"])
@require_auth
def list_documents():
    """List documents accessible to the current user.

    Public documents are always visible. Non-public documents are only
    visible if the user is a member of an access group linked to the
    document, or if the user is an admin.
    """
    user = g.current_user
    user_id = str(user.id)

    if user.role == "admin":
        docs = Document_.objects()
        return jsonify([d.to_dict() for d in docs])

    user_group_ids = []
    groups = UserGroup.objects(is_active=True)
    for grp in groups:
        if user_id in grp.user_ids or user_id in grp.curator_ids:
            user_group_ids.append(str(grp.id))

    accessible = []
    for doc in Document_.objects():
        if doc.is_public:
            accessible.append(doc)
            continue
        for gid in doc.access_group_ids:
            if gid in user_group_ids:
                accessible.append(doc)
                break

    return jsonify([d.to_dict() for d in accessible])


@app.route("/api/manage/documents/<doc_id>", methods=["GET"])
@require_auth
def get_document(doc_id):
    doc = Document_.objects(id=doc_id).first()
    if not doc:
        return jsonify({"detail": "Document not found"}), 404

    user = g.current_user
    user_id = str(user.id)

    if user.role == "admin":
        return jsonify(doc.to_dict())

    if doc.is_public:
        return jsonify(doc.to_dict())

    user_group_ids = []
    groups = UserGroup.objects(is_active=True)
    for grp in groups:
        if user_id in grp.user_ids or user_id in grp.curator_ids:
            user_group_ids.append(str(grp.id))

    for gid in doc.access_group_ids:
        if gid in user_group_ids:
            return jsonify(doc.to_dict())

    return jsonify({"detail": "Access denied"}), 403


# ---- Seed data ----

def seed_database():
    flag = os.getenv("FLAG", "flag{placeholder}")

    User.drop_collection()
    UserGroup.drop_collection()
    ConnectorCredentialPair.drop_collection()
    Document_.drop_collection()

    admin_user = User(
        email="admin@onyx.app",
        hashed_password=User.hash_password("Kj8#mP2$vL9xQ4!nR"),
        full_name="System Administrator",
        role="admin",
    ).save()

    curator_user = User(
        email="curator@onyx.app",
        hashed_password=User.hash_password("curator"),
        full_name="Sarah Chen",
        role="curator",
    ).save()

    basic_user1 = User(
        email="jdoe@onyx.app",
        hashed_password=User.hash_password("Yx7!kW3$bN8mF2@pJ"),
        full_name="John Doe",
        role="basic",
    ).save()

    basic_user2 = User(
        email="mwilson@onyx.app",
        hashed_password=User.hash_password("Tq5#hR9$cM4wE7!sU"),
        full_name="Maria Wilson",
        role="basic",
    ).save()

    cc_public = ConnectorCredentialPair(
        pair_id=1,
        connector_name="Web Connector",
        credential_name="web-default",
        is_public=True,
    ).save()

    cc_internal = ConnectorCredentialPair(
        pair_id=2,
        connector_name="Internal Wiki Connector",
        credential_name="wiki-service-account",
        is_public=False,
    ).save()

    cc_confidential = ConnectorCredentialPair(
        pair_id=3,
        connector_name="Secrets Vault Connector",
        credential_name="vault-admin-cred",
        is_public=False,
    ).save()

    eng_group = create_user_group(
        name="Engineering",
        description="Engineering team members",
        user_ids=[str(basic_user1.id)],
        curator_ids=[str(curator_user.id)],
        cc_pair_ids=[1, 2],
    )

    admin_group = create_user_group(
        name="Executive",
        description="Executive leadership and privileged access",
        user_ids=[str(admin_user.id)],
        curator_ids=[],
        cc_pair_ids=[1, 2, 3],
    )

    general_group = create_user_group(
        name="General",
        description="All company employees",
        user_ids=[str(basic_user1.id), str(basic_user2.id), str(curator_user.id)],
        curator_ids=[],
        cc_pair_ids=[1],
    )

    Document_(
        title="Company Handbook",
        content="Welcome to Onyx. This document contains general company policies and procedures.",
        source_connector="Web Connector",
        cc_pair_id=1,
        access_group_ids=[],
        is_public=True,
    ).save()

    Document_(
        title="Engineering Standards",
        content="Code review requirements: All PRs require two approvals. CI must pass before merge.",
        source_connector="Internal Wiki Connector",
        cc_pair_id=2,
        access_group_ids=[str(eng_group.id)],
        is_public=False,
    ).save()

    Document_(
        title="Infrastructure Credentials",
        content=flag,
        source_connector="Secrets Vault Connector",
        cc_pair_id=3,
        access_group_ids=[str(admin_group.id)],
        is_public=False,
    ).save()

    Document_(
        title="Q4 Planning Notes",
        content="Quarterly planning meeting notes: Focus areas include scaling infrastructure and improving search.",
        source_connector="Internal Wiki Connector",
        cc_pair_id=2,
        access_group_ids=[str(eng_group.id)],
        is_public=False,
    ).save()

    Document_(
        title="Onboarding Guide",
        content="New employee onboarding checklist: Set up development environment, complete security training.",
        source_connector="Web Connector",
        cc_pair_id=1,
        access_group_ids=[],
        is_public=True,
    ).save()


if __name__ == "__main__":
    seed_database()
    app.run(host="0.0.0.0", port=5013)
