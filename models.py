from sqlalchemy import Column, Integer, String, Date, Time, Float, ForeignKey, Numeric
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
    project = relationship("Project", back_populates="invoices")
