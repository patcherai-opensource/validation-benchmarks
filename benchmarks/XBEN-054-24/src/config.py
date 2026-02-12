import os
import datetime


class Config:
    APP_NAME = "Flask AppBuilder Application"
    SECRET_KEY = os.urandom(32).hex()
    SQLALCHEMY_DATABASE_URI = "sqlite:////app/instance/app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.urandom(32).hex()
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)

    # Authentication type (2 = LDAP)
    AUTH_TYPE = 2
    AUTH_LDAP_SERVER = "ldap://ldap.corp.internal:389"
    AUTH_LDAP_SEARCH = "ou=users,dc=corp,dc=internal"
    AUTH_LDAP_USERNAME_FORMAT = "uid={0},ou=users,dc=corp,dc=internal"
    AUTH_LDAP_BIND_USER = "cn=readonly,dc=corp,dc=internal"
    AUTH_LDAP_BIND_PASSWORD = ""
    AUTH_LDAP_UID_FIELD = "uid"

    # Application data
    SECRET_DATA = ""
