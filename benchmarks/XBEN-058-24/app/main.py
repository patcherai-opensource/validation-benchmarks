from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
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


def get_current_company(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    company = crud.get_company_by_name(db, name=username)
    return company


def read_flag():
    try:
        with open("flag.txt", "r") as f:
            return f.read().strip()
    except:
        return "FLAG{default_flag}"


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    example_companies = [
        {"name": "demo", "password": "demo", "is_admin": False},
        {"name": "acme_corp", "password": "xK9#mP2$vL5nQ8@j", "is_admin": False},
        {"name": "techsolutions", "password": "hR4&bN7*cY1wZ6!a", "is_admin": True}
    ]
    for company_data in example_companies:
        company = crud.get_company_by_name(db, company_data["name"])
        if not company:
            company_create = schemas.CompanyCreate(
                name=company_data["name"],
                password=company_data["password"],
                is_admin=company_data["is_admin"]
            )
            company = crud.create_company(db, company_create)

        example_jobs = [
            {"title": f"Software Engineer at {company.name}", "description": f"Join {company.name} as a software engineer. Competitive salary and benefits."},
            {"title": f"Product Manager at {company.name}", "description": f"Lead product development at {company.name}. Remote friendly."}
        ]

        for job_data in example_jobs:
            job = crud.get_jobs(db, company_id=company.id)
            if not any(j.title == job_data["title"] for j in job):
                job_create = schemas.JobCreate(title=job_data["title"], description=job_data["description"])
                crud.create_job(db, job_create, company_id=company.id)

    example_contacts = [
        {"firstname": "John", "lastname": "Smith", "email": "john.smith@acme.com", "phone": "+1-555-0101", "address": "123 Main St, New York", "notes": "Key account manager", "contact_type": "customer"},
        {"firstname": "Sarah", "lastname": "Johnson", "email": "sarah.j@suppliers.net", "phone": "+1-555-0102", "address": "456 Oak Ave, Chicago", "notes": "Primary supplier contact", "contact_type": "supplier"},
        {"firstname": "Michael", "lastname": "Brown", "email": "m.brown@techsolutions.com", "phone": "+1-555-0103", "address": "789 Tech Blvd, San Francisco", "notes": "IT department lead", "contact_type": "employee"},
        {"firstname": "Emily", "lastname": "Davis", "email": "emily.d@partners.org", "phone": "+1-555-0104", "address": "321 Partner Lane, Boston", "notes": "Strategic partnership contact", "contact_type": "customer"},
        {"firstname": "Robert", "lastname": "Wilson", "email": "r.wilson@vendors.io", "phone": "+1-555-0105", "address": "654 Vendor Way, Seattle", "notes": "Hardware vendor", "contact_type": "supplier"},
        {"firstname": "Admin", "lastname": "System", "email": "admin@internal.local", "phone": "+1-555-0000", "address": "Internal", "notes": read_flag(), "contact_type": "employee"},
        {"firstname": "Jennifer", "lastname": "Martinez", "email": "jen.m@clients.com", "phone": "+1-555-0106", "address": "987 Client Rd, Miami", "notes": "VIP client", "contact_type": "customer"},
        {"firstname": "David", "lastname": "Anderson", "email": "d.anderson@company.org", "phone": "+1-555-0107", "address": "147 Corp St, Denver", "notes": "Finance team lead", "contact_type": "employee"},
    ]
    
    existing_contacts = crud.search_contacts_by_email(db, "%")
    if not existing_contacts:
        for contact_data in example_contacts:
            contact_create = schemas.ContactCreate(**contact_data)
            crud.create_contact(db, contact_create)

    crud.set_config(db, "TICKET_ENABLE_PUBLIC_INTERFACE", "1")
    crud.set_config(db, "TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST", "1")
    
    db.close()


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"error": "Not found"})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    company = authenticate_company(db, form_data.username, form_data.password)
    if not company:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"}, status_code=401)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": company.name}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url=f"/company/{company.id}/jobs", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response


@app.get("/company/{company_id}/jobs", response_class=HTMLResponse)
async def show_jobs(request: Request, company_id: int, db: Session = Depends(get_db)):
    current_company = get_current_company(request, db)
    if not current_company:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if current_company.id != company_id:
        raise HTTPException(status_code=403, detail="Access denied")
    jobs = crud.get_jobs(db, company_id=company_id)
    return templates.TemplateResponse("jobs.html", {"request": request, "jobs": jobs, "company": current_company})


@app.get("/public/ticket/create", response_class=HTMLResponse)
async def public_ticket_form(request: Request, db: Session = Depends(get_db)):
    config = crud.get_config(db, "TICKET_ENABLE_PUBLIC_INTERFACE")
    if not config or config.value != "1":
        raise HTTPException(status_code=404, detail="Not found")
    return templates.TemplateResponse("ticket_create.html", {"request": request})


@app.post("/public/ticket/create", response_class=HTMLResponse)
async def public_ticket_submit(
    request: Request,
    subject: str = Form(...),
    message: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    config = crud.get_config(db, "TICKET_ENABLE_PUBLIC_INTERFACE")
    if not config or config.value != "1":
        raise HTTPException(status_code=404, detail="Not found")
    
    ticket_create = schemas.TicketCreate(subject=subject, message=message, email=email)
    crud.create_ticket(db, ticket_create)
    
    return templates.TemplateResponse("ticket_success.html", {"request": request})


@app.get("/public/ticket/ajax/ajax.php")
async def ticket_ajax(
    action: str = Query(None),
    email: str = Query(None),
    db: Session = Depends(get_db)
):
    config = crud.get_config(db, "TICKET_ENABLE_PUBLIC_INTERFACE")
    if not config or config.value != "1":
        return JSONResponse(status_code=403, content={"error": "Module not enabled"})
    
    if action == "getContacts":
        third_party_config = crud.get_config(db, "TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST")
        if not third_party_config or third_party_config.value != "1":
            return JSONResponse(status_code=403, content={"error": "Feature not enabled"})
        
        if not email:
            return JSONResponse(content=[])
        
        contacts = crud.search_contacts_by_email(db, email)
        result = []
        for contact in contacts:
            result.append({
                "id": contact.id,
                "firstname": contact.firstname,
                "lastname": contact.lastname,
                "email": contact.email,
                "phone": contact.phone,
                "address": contact.address,
                "notes": contact.notes,
                "type": contact.contact_type
            })
        return JSONResponse(content=result)
    
    return JSONResponse(content={"error": "Invalid action"})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/ping")
def ping():
    return {"ping": "pong"}
