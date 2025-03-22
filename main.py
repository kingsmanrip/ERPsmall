from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, Base, get_db
from models import User, Employee, DailyEntry, Payroll, Project, Invoice
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from typing import Optional
import io
from weasyprint import HTML
from decimal import Decimal
from jose import jwt, JWTError

app = FastAPI(title="Mauricio Paint and Dry Wall Financial System")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
Base.metadata.create_all(bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Get current user from cookie or header
async def get_current_user_from_cookie_or_token(request: Request, db: Session = Depends(get_db)):
    # First try to get token from cookie
    token = request.cookies.get("access_token")
    
    # If not in cookie, try to get from Authorization header
    if not token and "Authorization" in request.headers:
        auth = request.headers["Authorization"]
        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # If token starts with "bearer ", remove it
    if token.lower().startswith("bearer "):
        token = token[7:]
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

# Pydantic models for request validation
class DailyEntryCreate(BaseModel):
    employee_id: int
    date: date
    entry_time: str  # Format: "HH:MM"
    exit_time: str   # Format: "HH:MM"
    lunch_duration: int

class InvoiceCreate(BaseModel):
    project_id: int
    invoice_number: str
    total_amount: float

class ProjectCreate(BaseModel):
    name: str
    materials_cost: float
    labor_cost: float
    amount_charged: float

# Authentication endpoint
@app.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    # Set the token as a cookie
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Login page
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "company_name": "Mauricio Paint and Dry Wall"})

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    # Calculate total payroll for the last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    total_payroll = db.query(func.sum(Payroll.amount_paid)).filter(Payroll.period_end >= thirty_days_ago).scalar() or 0
    
    # Count active projects
    active_projects = db.query(Project).count()
    
    # Get recent payrolls
    recent_payrolls = db.query(Payroll).join(Employee).order_by(Payroll.period_end.desc()).limit(5).all()
    
    # Get recent invoices
    recent_invoices = db.query(Invoice).join(Project).order_by(Invoice.issue_date.desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": current_user.username,
        "total_payroll": total_payroll,
        "active_projects": active_projects,
        "recent_payrolls": recent_payrolls,
        "recent_invoices": recent_invoices
    })

# Timesheet entry page
@app.get("/timesheets", response_class=HTMLResponse)
async def timesheets_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    employees = db.query(Employee).all()
    today = datetime.now().date()
    # Calculate the date of the most recent Friday
    friday = today - timedelta(days=(today.weekday() - 4) % 7)
    # Calculate the Monday of that week
    week_start = friday - timedelta(days=4)
    
    return templates.TemplateResponse("timesheets.html", {
        "request": request,
        "employees": employees,
        "week_start": week_start,
        "friday": friday,
        "timedelta": timedelta  # Pass timedelta to the template
    })

@app.post("/daily-entries")
async def create_daily_entry(
    employee_id: int = Form(...),
    date: str = Form(...),
    entry_time: str = Form(...),
    exit_time: str = Form(...),
    lunch_duration: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    # Convert string inputs to appropriate types
    entry_date = datetime.strptime(date, "%Y-%m-%d").date()
    entry_time_obj = datetime.strptime(entry_time, "%H:%M").time()
    exit_time_obj = datetime.strptime(exit_time, "%H:%M").time()
    
    # Check if entry already exists for this employee and date
    existing_entry = db.query(DailyEntry).filter(
        DailyEntry.employee_id == employee_id,
        DailyEntry.date == entry_date
    ).first()
    
    if existing_entry:
        # Update existing entry
        existing_entry.entry_time = entry_time_obj
        existing_entry.exit_time = exit_time_obj
        existing_entry.lunch_duration = lunch_duration
    else:
        # Create new entry
        entry = DailyEntry(
            employee_id=employee_id,
            date=entry_date,
            entry_time=entry_time_obj,
            exit_time=exit_time_obj,
            lunch_duration=lunch_duration
        )
        db.add(entry)
    
    db.commit()
    return RedirectResponse(url="/timesheets", status_code=303)

# Projects management
@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    projects = db.query(Project).all()
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": projects
    })

@app.post("/projects")
async def create_project(
    name: str = Form(...),
    materials_cost: float = Form(...),
    labor_cost: float = Form(...),
    amount_charged: float = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    project = Project(
        name=name,
        materials_cost=Decimal(str(materials_cost)),
        labor_cost=Decimal(str(labor_cost)),
        amount_charged=Decimal(str(amount_charged))
    )
    db.add(project)
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)

# Invoice creation and PDF download
@app.get("/invoices", response_class=HTMLResponse)
async def invoices_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    invoices = db.query(Invoice).all()
    projects = db.query(Project).all()
    return templates.TemplateResponse("invoices.html", {
        "request": request,
        "invoices": invoices,
        "projects": projects
    })

@app.post("/invoices")
async def create_invoice(
    project_id: int = Form(...),
    invoice_number: str = Form(...),
    total_amount: float = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    db_invoice = Invoice(
        project_id=project_id,
        invoice_number=invoice_number,
        issue_date=datetime.now().date(),
        total_amount=Decimal(str(total_amount))
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return RedirectResponse(url="/invoices", status_code=303)

@app.get("/invoices/{invoice_id}/pdf", response_class=StreamingResponse)
async def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    project = db.query(Project).filter(Project.id == invoice.project_id).first()
    
    # Render the invoice template
    html_content = templates.TemplateResponse(
        "invoice.html", 
        {
            "request": None,
            "invoice": invoice,
            "project": project,
            "company_name": "Mauricio Paint and Dry Wall",
            "issue_date": invoice.issue_date.strftime("%Y-%m-%d")
        }
    ).body.decode()
    
    # Generate PDF from HTML
    pdf = HTML(string=html_content).write_pdf()
    
    return StreamingResponse(
        io.BytesIO(pdf),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"}
    )

# Payroll management
@app.get("/payroll", response_class=HTMLResponse)
async def payroll_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    employees = db.query(Employee).all()
    payrolls = db.query(Payroll).order_by(Payroll.period_end.desc()).all()
    
    return templates.TemplateResponse("payroll.html", {
        "request": request,
        "employees": employees,
        "payrolls": payrolls
    })

@app.post("/payroll")
async def create_payroll(
    employee_id: int = Form(...),
    period_start: str = Form(...),
    period_end: str = Form(...),
    total_hours: float = Form(...),
    payment_method: str = Form(...),
    amount_paid: float = Form(...),
    deductions: Optional[float] = Form(0.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    payroll = Payroll(
        employee_id=employee_id,
        period_start=datetime.strptime(period_start, "%Y-%m-%d").date(),
        period_end=datetime.strptime(period_end, "%Y-%m-%d").date(),
        total_hours=total_hours,
        payment_method=payment_method,
        amount_paid=Decimal(str(amount_paid)),
        deductions=Decimal(str(deductions))
    )
    db.add(payroll)
    db.commit()
    return RedirectResponse(url="/payroll", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
