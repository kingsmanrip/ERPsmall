from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie, Response
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, Base, get_db
from models import User, Employee, DailyEntry, Payroll, Project, Invoice, Supplier, ExpenseCategory, AccountsPayable, AccountsPaid, MonthlyExpense
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta, date
import os
from fastapi import File, UploadFile
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
    # Check if session is active first
    session_active = request.cookies.get("session_active")
    if not session_active or session_active != "true":
        # Redirect to login page instead of showing an error
        return RedirectResponse(url="/login")
        
    # First try to get token from cookie
    token = request.cookies.get("access_token")
    
    # If not in cookie, try to get from Authorization header
    if not token and "Authorization" in request.headers:
        auth = request.headers["Authorization"]
        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            # Redirect to login page instead of showing an error
            return RedirectResponse(url="/login")
    
    if not token:
        # Redirect to login page instead of showing an error
        return RedirectResponse(url="/login")
    
    # If token starts with "bearer ", remove it
    if token.lower().startswith("bearer "):
        token = token[7:]
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # Redirect to login page instead of showing an error
            return RedirectResponse(url="/login")
    except JWTError:
        # Redirect to login page instead of showing an error
        return RedirectResponse(url="/login")
        
    # Get the user from the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        # Redirect to login page instead of showing an error
        return RedirectResponse(url="/login")
        
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
    
class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    
class ExpenseCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
class AccountsPayableCreate(BaseModel):
    supplier_id: int
    category_id: int
    description: str
    amount: float
    issue_date: date
    due_date: date
    payment_method: Optional[str] = None
    status: str = "Pending"
    notes: Optional[str] = None
    
class AccountsPaidCreate(BaseModel):
    supplier_id: int
    category_id: int
    description: str
    amount: float
    payment_date: date
    payment_method: str
    check_number: Optional[str] = None
    bank_name: Optional[str] = None
    notes: Optional[str] = None
    
class MonthlyExpenseCreate(BaseModel):
    category_id: int
    description: str
    amount: float
    expense_date: date
    payment_method: str
    notes: Optional[str] = None

# Authentication endpoint
@app.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Create access token with extended expiration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    # Set the token as a cookie with improved settings
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,  # Prevents JavaScript access
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",  # Protects against CSRF
        secure=False,  # Set to True in production with HTTPS
        path="/"  # Ensure cookie is available for all paths
    )
    
    # Also set a session cookie that doesn't expire with browser close
    response.set_cookie(
        key="session_active", 
        value="true",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
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
    # Using specific columns to avoid issues with schema mismatches
    recent_invoices = db.query(Invoice.id, Invoice.project_id, Invoice.invoice_number, 
                              Invoice.issue_date, Invoice.total_amount, Project.name.label('project_name'))\
                      .join(Project).order_by(Invoice.issue_date.desc()).limit(5).all()
    
    # Get upcoming payments (accounts payable)
    upcoming_payments = db.query(AccountsPayable).filter(AccountsPayable.status == "Pending").order_by(AccountsPayable.due_date).limit(5).all()
    
    # Calculate total accounts payable
    total_accounts_payable = db.query(func.sum(AccountsPayable.amount)).filter(AccountsPayable.status == "Pending").scalar() or 0
    
    # Calculate total monthly expenses for the current month
    first_day_of_month = datetime.now().replace(day=1).date()
    last_day_of_month = (datetime.now().replace(day=28) + timedelta(days=4)).replace(day=1).date() - timedelta(days=1)
    total_monthly_expenses = db.query(func.sum(MonthlyExpense.amount)).filter(
        MonthlyExpense.expense_date >= first_day_of_month,
        MonthlyExpense.expense_date <= last_day_of_month
    ).scalar() or 0
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": current_user.username,
        "total_payroll": total_payroll,
        "active_projects": active_projects,
        "recent_payrolls": recent_payrolls,
        "recent_invoices": recent_invoices,
        "upcoming_payments": upcoming_payments,
        "total_accounts_payable": total_accounts_payable,
        "total_monthly_expenses": total_monthly_expenses
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

# Financial Management - Suppliers
@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    suppliers = db.query(Supplier).all()
    return templates.TemplateResponse("suppliers.html", {
        "request": request,
        "suppliers": suppliers
    })

@app.post("/suppliers")
async def create_supplier(
    name: str = Form(...),
    contact_person: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    address: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    supplier = Supplier(
        name=name,
        contact_person=contact_person,
        phone=phone,
        email=email,
        address=address
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return RedirectResponse(url="/suppliers", status_code=303)

# Financial Management - Expense Categories
@app.get("/expense-categories", response_class=HTMLResponse)
async def expense_categories_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    categories = db.query(ExpenseCategory).all()
    return templates.TemplateResponse("expense_categories.html", {
        "request": request,
        "categories": categories
    })

@app.post("/expense-categories")
async def create_expense_category(
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    category = ExpenseCategory(
        name=name,
        description=description
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return RedirectResponse(url="/expense-categories", status_code=303)

# Financial Management - Accounts Payable
@app.get("/accounts-payable", response_class=HTMLResponse)
async def accounts_payable_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    accounts_payable = db.query(AccountsPayable).order_by(AccountsPayable.due_date).all()
    suppliers = db.query(Supplier).all()
    categories = db.query(ExpenseCategory).all()
    return templates.TemplateResponse("accounts_payable.html", {
        "request": request,
        "accounts_payable": accounts_payable,
        "suppliers": suppliers,
        "categories": categories,
        "payment_methods": ["Cash", "Check", "Transfer", "Card"],
        "statuses": ["Pending", "Paid"]
    })

@app.post("/accounts-payable")
async def create_accounts_payable(
    supplier_id: int = Form(...),
    category_id: int = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    issue_date: str = Form(...),
    due_date: str = Form(...),
    payment_method: str = Form(...),
    status: str = Form("Pending"),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    # Convert string dates to date objects
    issue_date_obj = datetime.strptime(issue_date, "%Y-%m-%d").date()
    due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
    
    account_payable = AccountsPayable(
        supplier_id=supplier_id,
        category_id=category_id,
        description=description,
        amount=amount,
        issue_date=issue_date_obj,
        due_date=due_date_obj,
        payment_method=payment_method,
        status=status,
        notes=notes
    )
    db.add(account_payable)
    db.commit()
    db.refresh(account_payable)
    return RedirectResponse(url="/accounts-payable", status_code=303)

@app.post("/accounts-payable/{id}/mark-as-paid")
async def mark_account_payable_as_paid(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    account_payable = db.query(AccountsPayable).filter(AccountsPayable.id == id).first()
    if not account_payable:
        raise HTTPException(status_code=404, detail="Account payable not found")
    
    account_payable.status = "Paid"
    db.commit()
    
    # Create an AccountsPaid record
    account_paid = AccountsPaid(
        supplier_id=account_payable.supplier_id,
        category_id=account_payable.category_id,
        description=account_payable.description,
        amount=account_payable.amount,
        payment_date=datetime.now().date(),
        payment_method=account_payable.payment_method,
        notes=f"Automatically created from accounts payable #{account_payable.id}"
    )
    db.add(account_paid)
    db.commit()
    
    return RedirectResponse(url="/accounts-payable", status_code=303)

# Financial Management - Accounts Paid
@app.get("/accounts-paid", response_class=HTMLResponse)
async def accounts_paid_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    accounts_paid = db.query(AccountsPaid).order_by(AccountsPaid.payment_date.desc()).all()
    suppliers = db.query(Supplier).all()
    categories = db.query(ExpenseCategory).all()
    return templates.TemplateResponse("accounts_paid.html", {
        "request": request,
        "accounts_paid": accounts_paid,
        "suppliers": suppliers,
        "categories": categories,
        "payment_methods": ["Cash", "Check", "Transfer", "Card"]
    })

@app.post("/accounts-paid")
async def create_accounts_paid(
    supplier_id: int = Form(...),
    category_id: int = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: str = Form(...),
    check_number: str = Form(None),
    bank_name: str = Form(None),
    notes: str = Form(None),
    receipt: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    # Convert string date to date object
    payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d").date()
    
    # Handle receipt file upload if provided
    receipt_file_path = None
    if receipt and receipt.filename:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Generate a unique filename
        file_extension = os.path.splitext(receipt.filename)[1]
        unique_filename = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
        file_path = os.path.join("uploads", unique_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(await receipt.read())
        
        receipt_file_path = file_path
    
    account_paid = AccountsPaid(
        supplier_id=supplier_id,
        category_id=category_id,
        description=description,
        amount=amount,
        payment_date=payment_date_obj,
        payment_method=payment_method,
        check_number=check_number if payment_method == "Check" else None,
        bank_name=bank_name if payment_method in ["Check", "Transfer"] else None,
        receipt_file=receipt_file_path,
        notes=notes
    )
    db.add(account_paid)
    db.commit()
    db.refresh(account_paid)
    return RedirectResponse(url="/accounts-paid", status_code=303)

# Financial Management - Monthly Expenses
@app.get("/monthly-expenses", response_class=HTMLResponse)
async def monthly_expenses_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    monthly_expenses = db.query(MonthlyExpense).order_by(MonthlyExpense.expense_date.desc()).all()
    categories = db.query(ExpenseCategory).all()
    return templates.TemplateResponse("monthly_expenses.html", {
        "request": request,
        "monthly_expenses": monthly_expenses,
        "categories": categories,
        "payment_methods": ["Cash", "Check", "Transfer", "Card"]
    })

@app.post("/monthly-expenses")
async def create_monthly_expense(
    category_id: int = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    expense_date: str = Form(...),
    payment_method: str = Form(...),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    # Convert string date to date object
    expense_date_obj = datetime.strptime(expense_date, "%Y-%m-%d").date()
    
    monthly_expense = MonthlyExpense(
        category_id=category_id,
        description=description,
        amount=amount,
        expense_date=expense_date_obj,
        payment_method=payment_method,
        notes=notes
    )
    db.add(monthly_expense)
    db.commit()
    db.refresh(monthly_expense)
    return RedirectResponse(url="/monthly-expenses", status_code=303)

# Financial Reports
@app.get("/financial-reports", response_class=HTMLResponse)
async def financial_reports_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie_or_token)):
    return templates.TemplateResponse("financial_reports.html", {
        "request": request
    })

@app.get("/api/reports/accounts-payable")
async def get_accounts_payable_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    query = db.query(AccountsPayable).join(Supplier).join(ExpenseCategory)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(AccountsPayable.due_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(AccountsPayable.due_date <= end_date_obj)
    
    if supplier_id:
        query = query.filter(AccountsPayable.supplier_id == supplier_id)
    
    if category_id:
        query = query.filter(AccountsPayable.category_id == category_id)
    
    if status:
        query = query.filter(AccountsPayable.status == status)
    
    accounts_payable = query.all()
    
    # Convert to dict for JSON response
    result = []
    for ap in accounts_payable:
        result.append({
            "id": ap.id,
            "supplier": ap.supplier.name,
            "category": ap.category.name,
            "description": ap.description,
            "amount": float(ap.amount),
            "issue_date": ap.issue_date.isoformat(),
            "due_date": ap.due_date.isoformat(),
            "payment_method": ap.payment_method,
            "status": ap.status,
            "notes": ap.notes
        })
    
    return result

@app.get("/api/reports/accounts-paid")
async def get_accounts_paid_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    supplier_id: Optional[int] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    query = db.query(AccountsPaid).join(Supplier).join(ExpenseCategory)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(AccountsPaid.payment_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(AccountsPaid.payment_date <= end_date_obj)
    
    if supplier_id:
        query = query.filter(AccountsPaid.supplier_id == supplier_id)
    
    if category_id:
        query = query.filter(AccountsPaid.category_id == category_id)
    
    if payment_method:
        query = query.filter(AccountsPaid.payment_method == payment_method)
    
    accounts_paid = query.all()
    
    # Convert to dict for JSON response
    result = []
    for ap in accounts_paid:
        result.append({
            "id": ap.id,
            "supplier": ap.supplier.name,
            "category": ap.category.name,
            "description": ap.description,
            "amount": float(ap.amount),
            "payment_date": ap.payment_date.isoformat(),
            "payment_method": ap.payment_method,
            "check_number": ap.check_number,
            "bank_name": ap.bank_name,
            "notes": ap.notes
        })
    
    return result

@app.get("/api/reports/monthly-expenses")
async def get_monthly_expenses_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    query = db.query(MonthlyExpense).join(ExpenseCategory)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(MonthlyExpense.expense_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(MonthlyExpense.expense_date <= end_date_obj)
    
    if category_id:
        query = query.filter(MonthlyExpense.category_id == category_id)
    
    if payment_method:
        query = query.filter(MonthlyExpense.payment_method == payment_method)
    
    monthly_expenses = query.all()
    
    # Convert to dict for JSON response
    result = []
    for me in monthly_expenses:
        result.append({
            "id": me.id,
            "category": me.category.name,
            "description": me.description,
            "amount": float(me.amount),
            "expense_date": me.expense_date.isoformat(),
            "payment_method": me.payment_method,
            "notes": me.notes
        })
    
    return result

@app.get("/api/reports/payment-methods")
async def get_payment_methods_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    # Initialize query for accounts paid by payment method
    ap_query = db.query(
        AccountsPaid.payment_method,
        func.sum(AccountsPaid.amount).label("total")
    ).group_by(AccountsPaid.payment_method)
    
    # Initialize query for monthly expenses by payment method
    me_query = db.query(
        MonthlyExpense.payment_method,
        func.sum(MonthlyExpense.amount).label("total")
    ).group_by(MonthlyExpense.payment_method)
    
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        ap_query = ap_query.filter(AccountsPaid.payment_date >= start_date_obj)
        me_query = me_query.filter(MonthlyExpense.expense_date >= start_date_obj)
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        ap_query = ap_query.filter(AccountsPaid.payment_date <= end_date_obj)
        me_query = me_query.filter(MonthlyExpense.expense_date <= end_date_obj)
    
    # Execute queries
    accounts_paid_by_method = {pm: float(total) for pm, total in ap_query.all()}
    expenses_by_method = {pm: float(total) for pm, total in me_query.all()}
    
    # Combine results
    payment_methods = set(list(accounts_paid_by_method.keys()) + list(expenses_by_method.keys()))
    result = []
    
    for method in payment_methods:
        result.append({
            "payment_method": method,
            "accounts_paid_total": accounts_paid_by_method.get(method, 0),
            "expenses_total": expenses_by_method.get(method, 0),
            "combined_total": accounts_paid_by_method.get(method, 0) + expenses_by_method.get(method, 0)
        })
    
    return result

@app.get("/api/reports/payment-forecast")
async def get_payment_forecast_report(
    days: Optional[int] = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_token)
):
    today = datetime.now().date()
    forecast_end = today + timedelta(days=days)
    
    # Get all pending accounts payable due within the forecast period
    query = db.query(AccountsPayable).join(Supplier).filter(
        AccountsPayable.status == "Pending",
        AccountsPayable.due_date >= today,
        AccountsPayable.due_date <= forecast_end
    ).order_by(AccountsPayable.due_date)
    
    accounts_payable = query.all()
    
    # Convert to dict for JSON response
    result = []
    for ap in accounts_payable:
        days_until_due = (ap.due_date - today).days
        alert_level = "high" if days_until_due <= 7 else "medium" if days_until_due <= 14 else "low"
        
        result.append({
            "id": ap.id,
            "supplier": ap.supplier.name,
            "description": ap.description,
            "amount": float(ap.amount),
            "due_date": ap.due_date.isoformat(),
            "days_until_due": days_until_due,
            "alert_level": alert_level
        })
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
