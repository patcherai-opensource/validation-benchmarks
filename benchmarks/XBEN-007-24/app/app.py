from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_graphql import GraphQLView
import graphene
import os

app = Flask(__name__)
app.secret_key = '@#$%^R&GYUIUBJIU#@*DF&G*H'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///irrd.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

PASSWORD_HASHERS = {
    'MD5-PW': 'md5_crypt',
    'CRYPT-PW': 'crypt',
    'BCRYPT-PW': 'bcrypt',
}

def remove_auth_hashes(text):
    """
    Remove password hashes from auth lines in RPSL object text.
    This sanitizes mntner objects before returning them to users.
    """
    if not text:
        return text
    
    lines = text.split('\n')
    sanitized_lines = []
    
    for line in lines:
        sanitized = False
        for hash_name in PASSWORD_HASHERS.keys():
            if line.strip().startswith(f'auth: {hash_name}'):
                sanitized_lines.append(f'auth: {hash_name} <hash removed>')
                sanitized = True
                break
        if not sanitized:
            sanitized_lines.append(line)
    
    return '\n'.join(sanitized_lines)


def remove_auth_hashes_from_list(auth_list):
    """
    Remove password hashes from a list of auth attribute values.
    """
    if not auth_list:
        return auth_list
    
    sanitized = []
    for auth_value in auth_list:
        is_hash = False
        for hash_name in PASSWORD_HASHERS.keys():
            if auth_value.startswith(hash_name):
                sanitized.append(f'{hash_name} <hash removed>')
                is_hash = True
                break
        if not is_hash:
            sanitized.append(auth_value)
    
    return sanitized


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class Maintainer(db.Model):
    """RPSL mntner (maintainer) object"""
    id = db.Column(db.Integer, primary_key=True)
    mntner = db.Column(db.String(80), unique=True, nullable=False)
    descr = db.Column(db.String(200), nullable=False)
    admin_c = db.Column(db.String(80), nullable=False)
    tech_c = db.Column(db.String(80), nullable=False)
    upd_to = db.Column(db.String(120), nullable=False)
    auth = db.Column(db.Text, nullable=False)
    mnt_by = db.Column(db.String(80), nullable=False)
    source = db.Column(db.String(40), nullable=False)
    
    def get_object_text(self):
        """Return the full RPSL object as text"""
        return f"""mntner: {self.mntner}
descr: {self.descr}
admin-c: {self.admin_c}
tech-c: {self.tech_c}
upd-to: {self.upd_to}
auth: {self.auth}
mnt-by: {self.mnt_by}
source: {self.source}"""

    def get_auth_list(self):
        """Return auth attributes as a list"""
        return [self.auth]


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

# GraphQL Schema for RPSL Objects

class MaintainerType(graphene.ObjectType):
    """GraphQL type for mntner (maintainer) RPSL objects"""
    id = graphene.Int()
    mntner = graphene.String()
    descr = graphene.String()
    admin_c = graphene.String()
    tech_c = graphene.String()
    upd_to = graphene.String()
    auth = graphene.List(graphene.String)
    mnt_by = graphene.String()
    source = graphene.String()
    object_text = graphene.String()


class Query(graphene.ObjectType):
    rpsl_objects = graphene.List(
        MaintainerType, 
        rpsl_pk=graphene.String(required=False),
        sources=graphene.List(graphene.String, required=False)
    )
    
    def resolve_rpsl_objects(self, info, rpsl_pk=None, sources=None):
        query = Maintainer.query
        
        if rpsl_pk:
            query = query.filter_by(mntner=rpsl_pk)
        
        if sources:
            query = query.filter(Maintainer.source.in_(sources))
        
        maintainers = query.all()
        
        result = []
        for m in maintainers:
            sanitized_object_text = remove_auth_hashes(m.get_object_text())
            sanitized_auth = remove_auth_hashes_from_list(m.get_auth_list())
            
            result.append(MaintainerType(
                id=m.id,
                mntner=m.mntner,
                descr=m.descr,
                admin_c=m.admin_c,
                tech_c=m.tech_c,
                upd_to=m.upd_to,
                auth=sanitized_auth,
                mnt_by=m.mnt_by,
                source=m.source,
                object_text=sanitized_object_text
            ))
        
        return result


class CreateMaintainer(graphene.Mutation):
    class Arguments:
        mntner = graphene.String(required=True)
        descr = graphene.String(required=True)
        admin_c = graphene.String(required=True)
        tech_c = graphene.String(required=True)
        upd_to = graphene.String(required=True)
        auth = graphene.String(required=True)
        mnt_by = graphene.String(required=True)
        source = graphene.String(required=True)

    maintainer = graphene.Field(MaintainerType)

    def mutate(self, info, mntner, descr, admin_c, tech_c, upd_to, auth, mnt_by, source):
        new_mnt = Maintainer(
            mntner=mntner,
            descr=descr,
            admin_c=admin_c,
            tech_c=tech_c,
            upd_to=upd_to,
            auth=auth,
            mnt_by=mnt_by,
            source=source
        )
        db.session.add(new_mnt)
        db.session.commit()
        
        sanitized_auth = remove_auth_hashes_from_list([auth])
        sanitized_object_text = remove_auth_hashes(new_mnt.get_object_text())
        
        return CreateMaintainer(maintainer=MaintainerType(
            id=new_mnt.id,
            mntner=new_mnt.mntner,
            descr=new_mnt.descr,
            admin_c=new_mnt.admin_c,
            tech_c=new_mnt.tech_c,
            upd_to=new_mnt.upd_to,
            auth=sanitized_auth,
            mnt_by=new_mnt.mnt_by,
            source=new_mnt.source,
            object_text=sanitized_object_text
        ))


class Mutation(graphene.ObjectType):
    create_maintainer = CreateMaintainer.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.password == data['password']:
            login_user(user)
            return jsonify({"message": "Login successful", "userID": user.id})
        return jsonify({"message": "Invalid credentials"}), 401

    if current_user.is_authenticated:
        return redirect(url_for('manage_objects'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/manage', methods=['GET'])
@login_required
def manage_objects():
    return render_template('manage_objects.html', userID=current_user.id)


@app.route('/view', methods=['GET'])
@login_required
def view_objects():
    user = current_user
    maintainers = Maintainer.query.all()
    return render_template('view_objects.html', userID=current_user.id, username=user.username, maintainers=maintainers)


def init_db():
    db.drop_all()
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        user1 = User(username='admin', password='irrd_admin_2024')
        db.session.add(user1)
        db.session.commit()

    if not User.query.filter_by(username='operator').first():
        user2 = User(username='operator', password='operator')
        db.session.add(user2)
        db.session.commit()

    flag = os.getenv('FLAG', 'FLAG{test_flag_placeholder}')

    if Maintainer.query.count() == 0:
        mnt1 = Maintainer(
            mntner='RIPE-NCC-HM-MNT',
            descr='RIPE NCC Hostmaster',
            admin_c='DUMY-RIPE',
            tech_c='DUMY-RIPE',
            upd_to='hostmaster@ripe.net',
            auth='MD5-PW $1$SaltVal1$hashedpassword123456789',
            mnt_by='RIPE-NCC-HM-MNT',
            source='RIPE'
        )
        db.session.add(mnt1)
        
        mnt2 = Maintainer(
            mntner='AS1234-MNT',
            descr='Example Network Maintainer',
            admin_c='JD1-RIPE',
            tech_c='JD1-RIPE',
            upd_to='noc@example.net',
            auth='BCRYPT-PW $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.NGU7vdVkCKIKJy',
            mnt_by='AS1234-MNT',
            source='RIPE'
        )
        db.session.add(mnt2)
        
        mnt3 = Maintainer(
            mntner='ARIN-MNT',
            descr='ARIN Registry',
            admin_c='ARIN-CONTACT',
            tech_c='ARIN-CONTACT',
            upd_to='hostmaster@arin.net',
            auth='MD5-PW $1$ArInSaLt$K8vJnhXuB3mF2pA9wE1rQ0',
            mnt_by='ARIN-MNT',
            source='ARIN'
        )
        db.session.add(mnt3)
        
        mnt4 = Maintainer(
            mntner='LEGACY-NET-MNT',
            descr='Legacy Network Services',
            admin_c='LN-ADMIN',
            tech_c='LN-TECH',
            upd_to='admin@legacy-network.com',
            auth=f'md5-pw {flag}',
            mnt_by='LEGACY-NET-MNT',
            source='RIPE'
        )
        db.session.add(mnt4)
        
        mnt5 = Maintainer(
            mntner='APNIC-HM-MNT',
            descr='APNIC Hostmaster',
            admin_c='APNIC-HM',
            tech_c='APNIC-HM',
            upd_to='hostmaster@apnic.net',
            auth='CRYPT-PW abcDEFghiJKL12',
            mnt_by='APNIC-HM-MNT',
            source='APNIC'
        )
        db.session.add(mnt5)
        
        mnt6 = Maintainer(
            mntner='TRANSIT-PEER-MNT',
            descr='Transit Peering Network',
            admin_c='TP-ADMIN',
            tech_c='TP-NOC',
            upd_to='peering@transit.net',
            auth='bcrypt-pw $2b$12$AnotherHashThatShouldBeHidden',
            mnt_by='TRANSIT-PEER-MNT',
            source='RIPE'
        )
        db.session.add(mnt6)
        
        mnt7 = Maintainer(
            mntner='CLOUD-PROVIDER-MNT',
            descr='Cloud Infrastructure Provider',
            admin_c='CP-NOC',
            tech_c='CP-NOC',
            upd_to='noc@cloudprovider.io',
            auth='MD5-PW $1$CloudSlt$hF8gK2mN4pQ6rT0uW9xY1z',
            mnt_by='CLOUD-PROVIDER-MNT',
            source='RIPE'
        )
        db.session.add(mnt7)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db() 
    app.run(host='0.0.0.0', port=5003)

