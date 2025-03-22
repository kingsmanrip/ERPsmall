from sqlalchemy import Column, Integer, String, Date, Time, Float, ForeignKey, Numeric, Boolean, Text, DateTime
from decimal import Decimal
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Hashed password
    role = Column(String, default="accountant")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    hourly_rate = Column(Numeric(10, 2), default=20.0)
    daily_entries = relationship("DailyEntry", back_populates="employee")
    payrolls = relationship("Payroll", back_populates="employee")

class DailyEntry(Base):
    __tablename__ = "daily_entries"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    entry_time = Column(Time)
    exit_time = Column(Time)
    lunch_duration = Column(Integer)  # in minutes
    employee = relationship("Employee", back_populates="daily_entries")

    @property
    def worked_hours(self):
        entry_dt = datetime.combine(self.date, self.entry_time)
        exit_dt = datetime.combine(self.date, self.exit_time)
        total_time = (exit_dt - entry_dt).total_seconds() / 3600
        deduction = 0.5 if self.lunch_duration >= 30 else 0  # 30 minutes if lunch >= 30 min
        return total_time - deduction

class Payroll(Base):
    __tablename__ = "payrolls"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    total_hours = Column(Float)
    payment_method = Column(String)
    amount_paid = Column(Numeric(10, 2))
    deductions = Column(Numeric(10, 2), default=0.0)
    employee = relationship("Employee", back_populates="payrolls")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    materials_cost = Column(Numeric(10, 2), default=0.0)
    labor_cost = Column(Numeric(10, 2), default=0.0)
    amount_charged = Column(Numeric(10, 2))
    invoices = relationship("Invoice", back_populates="project")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    invoice_number = Column(String, unique=True)
    issue_date = Column(Date)
    total_amount = Column(Numeric(10, 2))
    paid = Column(Boolean, default=False)
    project = relationship("Project", back_populates="invoices")


class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    
    accounts_payable = relationship("AccountsPayable", back_populates="supplier")
    accounts_paid = relationship("AccountsPaid", back_populates="supplier")


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200))
    
    accounts_payable = relationship("AccountsPayable", back_populates="category")
    accounts_paid = relationship("AccountsPaid", back_populates="category")
    monthly_expenses = relationship("MonthlyExpense", back_populates="category")


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_method = Column(String(20))  # Cash, Check, Transfer, Card
    status = Column(String(20), default="Pending")  # Pending, Paid
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supplier = relationship("Supplier", back_populates="accounts_payable")
    category = relationship("ExpenseCategory", back_populates="accounts_payable")
    

class AccountsPaid(Base):
    __tablename__ = "accounts_paid"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(20), nullable=False)  # Cash, Check, Transfer, Card
    check_number = Column(String(50))  # For check payments
    bank_name = Column(String(100))  # For check/transfer payments
    receipt_file = Column(String(255))  # Path to uploaded receipt file
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    supplier = relationship("Supplier", back_populates="accounts_paid")
    category = relationship("ExpenseCategory", back_populates="accounts_paid")


class MonthlyExpense(Base):
    __tablename__ = "monthly_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"))
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    payment_method = Column(String(20), nullable=False)  # Cash, Check, Transfer, Card
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("ExpenseCategory", back_populates="monthly_expenses")
