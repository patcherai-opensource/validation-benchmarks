from datetime import timedelta, datetime
import os

from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Query
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
import crud, schemas
from database import SessionLocal, engine, Base

SECRET_KEY = "a very secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SupportDesk ERP v16.0.3 - Ticket Module Configuration
TICKET_MODULE_ENABLED = True
TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST = True  # Vulnerable config option

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SupportDesk ERP",
    description="Enterprise Resource Planning with Ticket Management",
    version="16.0.3"
)
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

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    # Initialize system configuration
    if not crud.get_config(db, "TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST"):
        crud.set_config(db, "TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST", "1")
    if not crud.get_config(db, "TICKET_MODULE_ENABLED"):
        crud.set_config(db, "TICKET_MODULE_ENABLED", "1")
    
    # Legacy company data (for backwards compatibility)
    example_companies = [
        {"name": "demo", "password": "demo", "is_admin": False},
        {"name": "admin", "password": "ajsdasd987asd87as7da9", "is_admin": True},
        {"name": "support", "password": "password3",  "is_admin": False}
    ]
    for company_data in example_companies:
        company = crud.get_company_by_name(db, company_data["name"])
        if not company:
            company_create = schemas.CompanyCreate(name=company_data["name"],
                                                   password=company_data["password"],
                                                   is_admin=company_data["is_admin"])
            company = crud.create_company(db, company_create)
    
    # Initialize contact database with sample data
    sample_contacts = [
        {"firstname": "John", "lastname": "Smith", "email": "john.smith@acmecorp.com", 
         "phone": "+1-555-0101", "company_name": "Acme Corporation", "contact_type": "customer",
         "notes": "Key account manager contact"},
        {"firstname": "Alice", "lastname": "Johnson", "email": "alice.j@supplier.net", 
         "phone": "+1-555-0102", "company_name": "Global Supplies Ltd", "contact_type": "supplier",
         "notes": "Primary supplier contact"},
        {"firstname": "Bob", "lastname": "Williams", "email": "bob.w@techpartner.io", 
         "phone": "+1-555-0103", "company_name": "Tech Partners Inc", "contact_type": "customer",
         "notes": "Technical support liaison"},
        {"firstname": "Carol", "lastname": "Davis", "email": "carol.d@internal.local", 
         "phone": "+1-555-0104", "company_name": "SupportDesk Internal", "contact_type": "employee",
         "notes": "Internal employee record"},
        {"firstname": "System", "lastname": "Administrator", "email": "sysadmin@internal.local", 
         "phone": "+1-555-0199", "company_name": "SupportDesk Internal", "contact_type": "confidential",
         "notes": os.getenv("FLAG", "FLAG{default_flag}")},  # Flag stored in confidential contact notes
    ]
    
    for contact_data in sample_contacts:
        existing = crud.search_contacts_by_email(db, contact_data["email"])
        if not existing:
            crud.create_contact(db, **contact_data)
    
    # Create sample tickets
    contacts = crud.search_contacts_by_email(db, "john.smith@acmecorp.com")
    if contacts:
        existing_tickets = crud.get_tickets(db)
        if not existing_tickets:
            crud.create_ticket(db, "Login issues", "Cannot access dashboard", contacts[0].id)
            crud.create_ticket(db, "Feature request", "Need export to PDF", contacts[0].id)
    
    db.close()


@app.post("/token", response_class=HTMLResponse)
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    company = authenticate_company(db, form_data.username, form_data.password)
    if not company:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": company.name}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard - requires authentication"""
    # Check for access token cookie
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/tickets", response_class=HTMLResponse)  
async def show_tickets(request: Request, db: Session = Depends(get_db)):
    """View tickets - requires authentication"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    tickets = crud.get_tickets(db)
    return templates.TemplateResponse("tickets.html", {"request": request, "tickets": tickets})

# ========================================================================
# PUBLIC TICKET ENDPOINTS - No authentication required
# These endpoints are publicly accessible for external ticket submission
# ========================================================================

@app.get("/public/ticket/create", response_class=HTMLResponse)
async def public_ticket_form(request: Request):
    """Public ticket creation form"""
    return templates.TemplateResponse("public_ticket.html", {"request": request})

@app.get("/public/ticket/ajax/ajax.php")
async def public_ticket_ajax(
    action: str = Query(None, description="Action to perform"),
    email: str = Query(None, description="Email address to search"),
    db: Session = Depends(get_db)
):
    """
    Public AJAX handler for ticket module
    Vulnerable endpoint - lacks proper authorization checks
    
    When TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST is enabled,
    this endpoint allows searching contacts without authentication.
    """
    
    if not TICKET_MODULE_ENABLED:
        return JSONResponse(
            status_code=403,
            content={"error": "Ticket module is disabled"}
        )
    
    if action == "getContacts":
        # VULNERABILITY: No authentication check when config option is enabled
        # This mirrors CVE-2023-33568 in Dolibarr
        if not TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST:
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied - contact creation option not enabled"}
            )
        
        if not email:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing email parameter"}
            )
        
        # VULNERABLE: email parameter passed directly to LIKE query
        # Using % as email will return ALL contacts (wildcard)
        contacts = crud.search_contacts_by_email(db, email)
        
        # Return contact data - includes sensitive 'notes' field
        result = []
        for contact in contacts:
            result.append({
                "id": contact.id,
                "firstname": contact.firstname,
                "lastname": contact.lastname,
                "email": contact.email,
                "phone": contact.phone,
                "company": contact.company_name,
                "type": contact.contact_type,
                "notes": contact.notes  # Sensitive data exposed!
            })
        
        return JSONResponse(content=result)
    
    elif action == "getTicketStatus":
        # Dummy action for plausibility
        return JSONResponse(content={"status": "available"})
    
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid action", "available_actions": ["getContacts", "getTicketStatus"]}
        )

@app.post("/public/ticket/submit")
async def public_ticket_submit(
    request: Request,
    subject: str = Form(...),
    description: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Submit a public ticket"""
    # Find or create contact
    contacts = crud.search_contacts_by_email(db, email)
    if contacts:
        contact_id = contacts[0].id
    else:
        # Create new contact if TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST is enabled
        if TICKET_CREATE_THIRD_PARTY_WITH_CONTACT_IF_NOT_EXIST:
            contact = crud.create_contact(db, "Guest", "User", email)
            contact_id = contact.id
        else:
            return JSONResponse(
                status_code=400, 
                content={"error": "Email not found in contacts database"}
            )
    
    ticket = crud.create_ticket(db, subject, description, contact_id)
    return JSONResponse(content={"success": True, "ticket_id": ticket.id})

# Legacy endpoints (kept for compatibility)
@app.get("/company/{company_id}/jobs", response_class=HTMLResponse)
async def show_jobs(request: Request, company_id: int, db: Session = Depends(get_db)):
    """Legacy endpoint - redirects to dashboard"""
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.get("/api/info")
def api_info():
    """API information endpoint"""
    return {
        "application": "SupportDesk ERP",
        "version": "16.0.3",
        "modules": {
            "ticket": TICKET_MODULE_ENABLED,
            "crm": True,
            "helpdesk": True
        },
        "public_endpoints": [
            "/public/ticket/create",
            "/public/ticket/ajax/ajax.php",
            "/public/ticket/submit"
        ]
    }
