from sqlalchemy.orm import Session
from models import User, DataTable, DataSchema, Instance
from schemas import UserCreate, TableCreate, SchemaCreate, InstanceCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()


def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(name=user.name, hashed_password=hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_tables(db: Session):
    return db.query(DataTable).all()


def get_table_by_name(db: Session, name: str):
    return db.query(DataTable).filter(DataTable.name == name).first()


def create_table(db: Session, table: TableCreate):
    db_table = DataTable(**table.dict())
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table


def get_all_schemas(db: Session):
    return db.query(DataSchema).all()


def get_schema_by_name(db: Session, name: str):
    return db.query(DataSchema).filter(DataSchema.name == name).first()


def create_schema(db: Session, schema: SchemaCreate):
    db_schema = DataSchema(**schema.dict())
    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)
    return db_schema


def get_all_instances(db: Session):
    return db.query(Instance).all()


def get_instance_by_name(db: Session, name: str):
    return db.query(Instance).filter(Instance.instance_name == name).first()


def create_instance(db: Session, instance: InstanceCreate):
    db_instance = Instance(**instance.dict())
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return db_instance
