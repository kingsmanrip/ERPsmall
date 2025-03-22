from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import User, Employee, Project, Supplier, ExpenseCategory, AccountsPayable, AccountsPaid, MonthlyExpense
from passlib.context import CryptContext
from decimal import Decimal
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create Patricia's user
    if not db.query(User).filter(User.username == "Patricia").first():
        hashed_password = pwd_context.hash("pati2025")
        user = User(username="Patricia", password=hashed_password, role="accountant")
        db.add(user)

    # Add sample employees
    if not db.query(Employee).first():
        employees = [
            Employee(name="John Doe", hourly_rate=20.0),
            Employee(name="Jane Smith", hourly_rate=22.0),
            Employee(name="Mike Johnson", hourly_rate=25.0)
        ]
        db.add_all(employees)
    
    # Add sample projects
    if not db.query(Project).first():
        projects = [
            Project(
                name="Residential Painting - 123 Main St", 
                materials_cost=1500.00, 
                labor_cost=2500.00, 
                amount_charged=5000.00
            ),
            Project(
                name="Commercial Drywall - Office Building", 
                materials_cost=3000.00, 
                labor_cost=4500.00, 
                amount_charged=9000.00
            )
        ]
        db.add_all(projects)
    
    # Add sample suppliers
    if not db.query(Supplier).first():
        suppliers = [
            Supplier(
                name="ABC Paint Supply",
                contact_person="John Smith",
                phone="555-123-4567",
                email="john@abcpaint.com",
                address="123 Supply St, Paintville, TX 12345"
            ),
            Supplier(
                name="XYZ Drywall Materials",
                contact_person="Jane Doe",
                phone="555-987-6543",
                email="jane@xyzdrywall.com",
                address="456 Material Ave, Drywall City, TX 67890"
            ),
            Supplier(
                name="Tools & More",
                contact_person="Mike Johnson",
                phone="555-456-7890",
                email="mike@toolsandmore.com",
                address="789 Hardware Blvd, Toolsville, TX 34567"
            )
        ]
        db.add_all(suppliers)
    
    # Add expense categories
    if not db.query(ExpenseCategory).first():
        categories = [
            ExpenseCategory(name="Materials", description="Paint, drywall, and other construction materials"),
            ExpenseCategory(name="Tools", description="Tools and equipment"),
            ExpenseCategory(name="Administrative", description="Office supplies and administrative expenses"),
            ExpenseCategory(name="Transportation", description="Fuel, vehicle maintenance, and transportation costs"),
            ExpenseCategory(name="Insurance", description="Business insurance expenses"),
            ExpenseCategory(name="Utilities", description="Electricity, water, and other utility expenses")
        ]
        db.add_all(categories)
        db.flush()  # Flush to get IDs for the categories
        
        # Get references to the added entities for sample data
        materials_category = db.query(ExpenseCategory).filter(ExpenseCategory.name == "Materials").first()
        tools_category = db.query(ExpenseCategory).filter(ExpenseCategory.name == "Tools").first()
        admin_category = db.query(ExpenseCategory).filter(ExpenseCategory.name == "Administrative").first()
        transport_category = db.query(ExpenseCategory).filter(ExpenseCategory.name == "Transportation").first()
        
        abc_supplier = db.query(Supplier).filter(Supplier.name == "ABC Paint Supply").first()
        xyz_supplier = db.query(Supplier).filter(Supplier.name == "XYZ Drywall Materials").first()
        tools_supplier = db.query(Supplier).filter(Supplier.name == "Tools & More").first()
        
        # Add sample accounts payable
        if not db.query(AccountsPayable).first():
            today = datetime.now().date()
            accounts_payable = [
                AccountsPayable(
                    supplier_id=abc_supplier.id,
                    category_id=materials_category.id,
                    description="Paint supplies for 123 Main St project",
                    amount=750.00,
                    issue_date=today - timedelta(days=5),
                    due_date=today + timedelta(days=25),
                    payment_method="Check",
                    status="Pending",
                    notes="Invoice #ABC-12345"
                ),
                AccountsPayable(
                    supplier_id=xyz_supplier.id,
                    category_id=materials_category.id,
                    description="Drywall materials for Office Building project",
                    amount=1200.00,
                    issue_date=today - timedelta(days=10),
                    due_date=today + timedelta(days=20),
                    payment_method="Transfer",
                    status="Pending",
                    notes="Invoice #XYZ-67890"
                ),
                AccountsPayable(
                    supplier_id=tools_supplier.id,
                    category_id=tools_category.id,
                    description="New power tools",
                    amount=500.00,
                    issue_date=today - timedelta(days=15),
                    due_date=today + timedelta(days=15),
                    payment_method="Card",
                    status="Pending",
                    notes="Invoice #TM-54321"
                )
            ]
            db.add_all(accounts_payable)
        
        # Add sample accounts paid
        if not db.query(AccountsPaid).first():
            accounts_paid = [
                AccountsPaid(
                    supplier_id=abc_supplier.id,
                    category_id=materials_category.id,
                    description="Paint supplies for previous project",
                    amount=500.00,
                    payment_date=today - timedelta(days=30),
                    payment_method="Check",
                    check_number="1234",
                    bank_name="First National Bank",
                    notes="Invoice #ABC-11111"
                ),
                AccountsPaid(
                    supplier_id=xyz_supplier.id,
                    category_id=materials_category.id,
                    description="Drywall materials for previous project",
                    amount=800.00,
                    payment_date=today - timedelta(days=45),
                    payment_method="Transfer",
                    bank_name="First National Bank",
                    notes="Invoice #XYZ-22222"
                )
            ]
            db.add_all(accounts_paid)
        
        # Add sample monthly expenses
        if not db.query(MonthlyExpense).first():
            monthly_expenses = [
                MonthlyExpense(
                    category_id=admin_category.id,
                    description="Office supplies",
                    amount=150.00,
                    expense_date=today - timedelta(days=15),
                    payment_method="Card",
                    notes="Purchased from Office Depot"
                ),
                MonthlyExpense(
                    category_id=transport_category.id,
                    description="Fuel for company vehicles",
                    amount=200.00,
                    expense_date=today - timedelta(days=10),
                    payment_method="Card",
                    notes="Fuel for the month"
                ),
                MonthlyExpense(
                    category_id=admin_category.id,
                    description="Internet and phone service",
                    amount=120.00,
                    expense_date=today - timedelta(days=5),
                    payment_method="Transfer",
                    notes="Monthly service bill"
                )
            ]
            db.add_all(monthly_expenses)

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
