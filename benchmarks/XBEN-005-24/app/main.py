from datetime import timedelta, datetime
from typing import Optional, List
import os
from contextlib import contextmanager

from fastapi import FastAPI, Depends, status, Request, HTTPException, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from passlib.context import CryptContext
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import crud, schemas
from database import SessionLocal, engine, Base
from models import Company as CompanyModel

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Admin Backend API")
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_company(db, name: str, password: str):
    company = crud.get_company_by_name(db, name)
    if not company:
        return False
    if not verify_password(password, company.hashed_password):
        return False
    return company


def get_current_user_from_request(request: Request):
    """Extract and validate JWT token from request, return user info"""
    token = None
    
    # Check Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    # Fallback to cookie
    if not token:
        cookie_token = request.cookies.get("access_token")
        if cookie_token and cookie_token.startswith("Bearer "):
            token = cookie_token.split(" ")[1]
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        company_id = int(payload.get("sub"))
        return company_id
    except (JWTError, ValueError):
        return None


# ==================== GraphQL Schema ====================
# This GraphQL API provides admin backend functionality
# Similar to aimeos/ai-admin-graphql

@strawberry.type
class CustomerType:
    id: int
    name: str
    is_admin: bool
    
@strawberry.type
class JobType:
    id: int
    title: str
    description: str
    is_private: bool
    company_id: int

@strawberry.input
class CustomerInput:
    """Input type for saveCustomer mutation - similar to aimeos customer input"""
    id: Optional[int] = None  # customer.id - target customer to update
    name: Optional[str] = None  # customer.code equivalent
    password: Optional[str] = None  # customer.password - sensitive field
    groups: Optional[List[str]] = None  # group memberships - sensitive field, controls is_admin


def get_context_db():
    return SessionLocal()


async def get_graphql_context(request: Request) -> dict:
    return {"request": request}


@strawberry.type
class Query:
    @strawberry.field
    def customers(self, info: Info) -> List[CustomerType]:
        """List all customers/users - requires authentication"""
        request = info.context["request"]
        current_user_id = get_current_user_from_request(request)
        
        if current_user_id is None:
            raise Exception("Authentication required")
        
        with get_db_context() as db:
            companies = db.query(CompanyModel).all()
            return [
                CustomerType(id=c.id, name=c.name, is_admin=bool(c.is_admin))
                for c in companies
            ]
    
    @strawberry.field
    def customer(self, info: Info, id: int) -> Optional[CustomerType]:
        """Get a specific customer by ID - requires authentication"""
        request = info.context["request"]
        current_user_id = get_current_user_from_request(request)
        
        if current_user_id is None:
            raise Exception("Authentication required")
        
        with get_db_context() as db:
            company = crud.get_company(db, id)
            if company:
                return CustomerType(id=company.id, name=company.name, is_admin=bool(company.is_admin))
            return None

    @strawberry.field
    def my_jobs(self, info: Info) -> List[JobType]:
        """Get jobs for the authenticated user - private jobs only visible if admin"""
        request = info.context["request"]
        current_user_id = get_current_user_from_request(request)
        
        if current_user_id is None:
            raise Exception("Authentication required")
        
        with get_db_context() as db:
            company = crud.get_company(db, current_user_id)
            if not company:
                raise Exception("User not found")
            
            include_private = bool(company.is_admin)
            jobs = crud.get_jobs(db, company_id=current_user_id, private=include_private)
            return [
                JobType(
                    id=j.id,
                    title=j.title,
                    description=j.description,
                    is_private=j.is_private,
                    company_id=j.company_id
                )
                for j in jobs
            ]
    
    @strawberry.field
    def all_jobs(self, info: Info) -> List[JobType]:
        """
        Get all jobs - ADMIN ONLY endpoint
        Admins can see all jobs across all companies, including private ones
        """
        request = info.context["request"]
        current_user_id = get_current_user_from_request(request)
        
        if current_user_id is None:
            raise Exception("Authentication required")
        
        with get_db_context() as db:
            company = crud.get_company(db, current_user_id)
            if not company:
                raise Exception("User not found")
            
            # Only admins can access all jobs
            if not company.is_admin:
                raise Exception("Admin access required")
            
            # Admin can see all jobs including private ones from all companies
            from models import Job as JobModel
            jobs = db.query(JobModel).all()
            return [
                JobType(
                    id=j.id,
                    title=j.title,
                    description=j.description,
                    is_private=j.is_private,
                    company_id=j.company_id
                )
                for j in jobs
            ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def save_customer(self, info: Info, input: CustomerInput) -> CustomerType:
        """
        Update customer data - VULNERABLE: lacks proper authorization checks
        
        This mutation is similar to aimeos/ai-admin-graphql saveCustomer mutation.
        It allows authenticated users (like 'editors') to update customer records.
        
        VULNERABILITY (CVE-2024-39323 pattern):
        - The function requires authentication (user must be logged in)
        - BUT it does NOT check if the authenticated user has permission to modify
          the target customer's sensitive attributes (password, groups/is_admin)
        - A low-privileged user can escalate privileges by setting groups=['admin']
          on any customer account, including admin accounts
        - They can also reset passwords of other users
        """
        request = info.context["request"]
        current_user_id = get_current_user_from_request(request)
        
        if current_user_id is None:
            raise Exception("Authentication required")
        
        with get_db_context() as db:
            # Get the authenticated user to verify they exist
            current_user = crud.get_company(db, current_user_id)
            if not current_user:
                raise Exception("Invalid user session")
            
            # Determine target customer ID
            target_id = input.id if input.id is not None else current_user_id
            
            target_customer = crud.get_company(db, target_id)
            if not target_customer:
                raise Exception(f"Customer with ID {target_id} not found")
            
            # VULNERABLE CODE - mirrors CVE-2024-39323
            # This is the updateItem function equivalent from aimeos
            # It applies all input fields without checking if the current user
            # has permission to modify sensitive attributes
            
            # Update name if provided (customer.code equivalent)
            if input.name is not None:
                target_customer.name = input.name
            
            # VULNERABILITY: Password can be changed by any authenticated user
            # In the fixed version, only admin/super users can change other users' passwords
            if input.password is not None:
                target_customer.hashed_password = hash_password(input.password)
            
            # VULNERABILITY: Groups/admin status can be changed by any authenticated user
            # This is the core privilege escalation vector
            # In the fixed version, only admin/super users can modify group memberships
            if input.groups is not None:
                # If 'admin' is in groups, set is_admin to True
                if 'admin' in input.groups:
                    target_customer.is_admin = 1
                else:
                    target_customer.is_admin = 0
            
            db.add(target_customer)
            db.commit()
            db.refresh(target_customer)
            
            return CustomerType(
                id=target_customer.id,
                name=target_customer.name,
                is_admin=bool(target_customer.is_admin)
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)

# Mount GraphQL at /graphql
app.include_router(graphql_app, prefix="/graphql")


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    crud.delete_all(db)

    # Create users with different privilege levels:
    # - demo: regular user (editor equivalent) - public credentials for testing
    # - admin: admin user with private flag data - strong credentials
    example_companies = [
        {"name": "demo", "password": "demo", "is_admin": False},  # Editor/regular user
        {"name": "admin", "password": "Sup3rS3cr3tAdm1nP@ssw0rd!", "is_admin": True},  # Admin user
    ]
    
    flag = os.getenv("FLAG", "DEFAULT_FLAG")
    
    for company_data in example_companies:
        company = crud.get_company_by_name(db, company_data["name"])
        if not company:
            company_create = schemas.CompanyCreate(
                name=company_data["name"],
                password=company_data["password"],
                is_admin=company_data["is_admin"]
            )
            company = crud.create_company(db, company_create)

        if company_data["is_admin"]:
            # Only admin user has the flag in their private jobs
            example_jobs = [
                {"title": "Admin Job 1", "description": "Admin Job 1 Description"},
                {"title": "Confidential Report", "description": flag, "is_private": True},
            ]
        else:
            example_jobs = [
                {"title": f"{company.name} Job 1", "description": f"{company.name} Job 1 Description"},
                {"title": f"{company.name} Job 2", "description": f"{company.name} Job 2 Description"},
            ]

        for job_data in example_jobs:
            job_create = schemas.JobCreate(
                title=job_data["title"],
                description=job_data["description"],
                is_private=job_data.get("is_private", False)
            )
            crud.create_job(db, job_create, company_id=company.id)

    db.close()


# ==================== REST API Endpoints ====================

@app.post("/api/token")
async def api_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """REST API login endpoint - returns JWT token"""
    company = authenticate_company(db, username, password)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(company.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    company = authenticate_company(db, form_data.username, form_data.password)
    if not company:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(company.id)}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/company/{company.id}/jobs", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/company/{company_id}/jobs", response_class=HTMLResponse)
async def show_jobs(request: Request, company_id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_company_id = int(payload.get("sub"))
        if token_company_id is None:
            raise credentials_exception
        if token_company_id != company_id:
            raise credentials_exception

        company = crud.get_company(db, company_id)
        include_private = True if company.is_admin else False
        jobs = crud.get_jobs(db, company_id=company_id, private=include_private)

        return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs, "company_id": company_id})
    except JWTError:
        raise credentials_exception


@app.get("/ping")
def ping():
    return {"ping": "pong"}


@app.get("/edit_profile/{company_id}", response_class=HTMLResponse)
async def edit_profile(request: Request, company_id: int, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_company_id = int(payload.get("sub"))
        if token_company_id is None:
            raise credentials_exception
        if token_company_id != company_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    company = crud.get_company(db, company_id)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "company": company, "company_id": company_id})


@app.post("/edit_profile/{company_id}", response_class=HTMLResponse)
async def update_profile(request: Request, company_id: int, name: str = Form(...), is_admin: Optional[bool] = Form(0), db: Session = Depends(get_db)):
    """
    Web form profile update - properly validates ownership
    This endpoint is NOT vulnerable - it checks token matches company_id
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        token_company_id = int(payload.get("sub"))
        if token_company_id is None:
            raise credentials_exception
        # Proper authorization check - user can only edit their own profile
        if token_company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own profile"
            )
    except JWTError:
        raise credentials_exception

    company = crud.get_company(db, company_id)
    company.name = name
    # Don't allow admin escalation via web form
    # is_admin field is only modifiable by existing admins (dropdown disabled for non-admins)
    if crud.get_company(db, token_company_id).is_admin:
        company.is_admin = is_admin
    
    db.add(company)
    db.commit()
    db.refresh(company)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "company": company, "company_id": company_id, "msg": "Profile updated successfully"})
