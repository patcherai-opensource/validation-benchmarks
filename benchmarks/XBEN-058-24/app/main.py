import os

from fastapi import FastAPI, Depends, Request, Form, status
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
import crud, schemas
from database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SupportFAQ Portal", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory="templates")

# Custom filter to render content without escaping (simulating missing sanitization)
# This is the vulnerability - user content is rendered as raw HTML
def unsafe_render(value):
    return Markup(value)

templates.env.filters['unsafe'] = unsafe_render

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Store flag in memory for internal API access
ADMIN_SECRET = os.getenv("FLAG", "FLAG{default_flag}")

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    
    # Create sample FAQ questions
    sample_questions = [
        {"question": "How do I reset my password?", "answer": "Click on 'Forgot Password' on the login page."},
        {"question": "What payment methods do you accept?", "answer": "We accept credit cards, PayPal, and bank transfers."},
        {"question": "How can I contact support?", "answer": "Email us at support@example.com or use the contact form."},
    ]
    
    for q_data in sample_questions:
        existing = crud.get_question_by_text(db, q_data["question"])
        if not existing:
            question = schemas.QuestionCreate(question=q_data["question"], answer=q_data.get("answer"))
            crud.create_question(db, question)
    
    db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Homepage with FAQ submission form and list of open questions"""
    questions = crud.get_all_questions(db)
    return templates.TemplateResponse("faq_home.html", {"request": request, "questions": questions})

@app.get("/questions", response_class=HTMLResponse)
async def view_questions(request: Request, db: Session = Depends(get_db)):
    """View all submitted questions - renders question content without sanitization"""
    questions = crud.get_all_questions(db)
    return templates.TemplateResponse("questions.html", {"request": request, "questions": questions})

@app.post("/submit", response_class=HTMLResponse)
async def submit_question(request: Request, question: str = Form(...), db: Session = Depends(get_db)):
    """Submit a new question - stored without sanitization"""
    question_create = schemas.QuestionCreate(question=question, answer=None)
    crud.create_question(db, question_create)
    return RedirectResponse(url="/questions?submitted=true", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/review")
async def admin_review(request: Request, db: Session = Depends(get_db)):
    """
    Admin review endpoint - simulates an admin viewing submitted questions.
    In a real scenario, an admin would browse this page, and any XSS in
    questions would execute in their browser context.
    
    For CTF purposes: This endpoint checks if any submitted question contains
    executable JavaScript. If XSS is detected, it simulates what would happen
    if an admin's browser executed the malicious code - returning the admin's
    sensitive session data (the flag).
    """
    import re
    import html
    
    questions = crud.get_all_questions(db)
    
    # Check for XSS patterns in questions
    # These patterns detect common XSS vectors
    xss_patterns = [
        r'<script[^>]*>',  # Script tags
        r'javascript:',     # JavaScript protocol
        r'on\w+\s*=',       # Event handlers (onclick, onerror, etc.)
        r'<img[^>]+onerror', # IMG with onerror
        r'<svg[^>]+onload',  # SVG with onload
        r'<iframe',          # Iframes
        r'<object',          # Object tags
        r'<embed',           # Embed tags
    ]
    
    xss_detected = False
    triggered_question = None
    
    for q in questions:
        for pattern in xss_patterns:
            if re.search(pattern, q.question, re.IGNORECASE):
                xss_detected = True
                triggered_question = q.question[:100]  # Truncate for display
                break
        if xss_detected:
            break
    
    if xss_detected:
        # XSS detected! In a real scenario, the malicious script would execute
        # in the admin's browser and could steal their session/cookies.
        # Simulating this by returning the admin's sensitive data.
        return JSONResponse(content={
            "status": "xss_executed",
            "message": "XSS payload executed in admin browser context!",
            "triggered_by": triggered_question,
            "exfiltrated_data": {
                "admin_session": ADMIN_SECRET,
                "cookie_data": f"session={ADMIN_SECRET}",
                "note": "In a real attack, this data would be sent to attacker's server"
            }
        })
    else:
        return JSONResponse(content={
            "status": "safe",
            "message": "Admin review completed. No malicious content detected.",
            "questions_reviewed": len(questions)
        })

@app.get("/ping")
def ping():
    return {"ping": "pong"}
