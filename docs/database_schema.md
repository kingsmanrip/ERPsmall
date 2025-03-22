# Database Schema

## Overview

The Mauricio Paint and Dry Wall Financial Management System uses a relational database to store all data related to employees, projects, timesheets, payroll, and invoices. This document provides a detailed description of the database schema, including tables, fields, relationships, and constraints.

## Entity Relationship Diagram

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│     User      │       │    Employee   │       │  DailyEntry   │
├───────────────┤       ├───────────────┤       ├───────────────┤
│ id            │       │ id            │       │ id            │
│ username      │       │ name          │◄──────┤ employee_id   │
│ password      │       │ hourly_rate   │       │ date          │
│ role          │       └───────────────┘       │ entry_time    │
└───────────────┘               │               │ exit_time     │
                                │               │ lunch_duration│
                                │               └───────────────┘
                                │                      │
                                ▼                      │
┌───────────────┐       ┌───────────────┐             │
│    Project    │       │    Payroll    │◄────────────┘
├───────────────┤       ├───────────────┤
│ id            │       │ id            │
│ name          │       │ employee_id   │
│ materials_cost│       │ period_start  │
│ labor_cost    │       │ period_end    │
│ amount_charged│       │ hours_worked  │
└───────────────┘       │ amount_paid   │
        │               │ payment_method│
        │               └───────────────┘
        ▼
┌───────────────┐
│    Invoice    │
├───────────────┤
│ id            │
│ project_id    │
│ invoice_number│
│ date          │
│ total_amount  │
│ paid          │
└───────────────┘

┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│   Supplier    │       │ExpenseCategory│       │AccountsPayable│
├───────────────┤       ├───────────────┤       ├───────────────┤
│ id            │       │ id            │       │ id            │
│ name          │◄──────┤ supplier_id   │◄──────┤ supplier_id   │
│ contact_person│       │ name          │       │ category_id   │
│ phone         │       │ description   │       │ description   │
│ email         │       └───────────────┘       │ amount        │
│ address       │               ▲               │ issue_date    │
└───────────────┘               │               │ due_date      │
        ▲                       │               │ payment_method│
        │                       │               │ status        │
        │                       │               │ notes         │
        │                       │               └───────────────┘
        │                       │
        │                       │
┌───────────────┐       ┌───────────────┐
│ AccountsPaid  │       │MonthlyExpense │
├───────────────┤       ├───────────────┤
│ id            │       │ id            │
│ supplier_id   │       │ category_id   │
│ category_id   │       │ description   │
│ description   │       │ amount        │
│ amount        │       │ expense_date  │
│ payment_date  │       │ payment_method│
│ payment_method│       │ notes         │
│ check_number  │       └───────────────┘
│ bank_name     │
│ receipt_file  │
│ notes         │
└───────────────┘
```

## Table Definitions

### User

The `User` table stores authentication and authorization information for system users.

| Column   | Type         | Constraints       | Description                           |
|----------|--------------|-------------------|---------------------------------------|
| id       | Integer      | PK, Auto-increment| Unique identifier for the user        |
| username | String(50)   | Unique, Not null  | Username for login                    |
| password | String(100)  | Not null          | Hashed password                       |
| role     | String(20)   | Not null          | User role (admin, accountant, etc.)   |

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    role = Column(String(20))
```

### Employee

The `Employee` table stores information about company employees.

| Column      | Type         | Constraints       | Description                           |
|-------------|--------------|-------------------|---------------------------------------|
| id          | Integer      | PK, Auto-increment| Unique identifier for the employee    |
| name        | String(100)  | Not null          | Employee's full name                  |
| hourly_rate | Numeric(10,2)| Not null          | Employee's hourly pay rate            |

```python
class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    hourly_rate = Column(Numeric(10, 2))
    
    daily_entries = relationship("DailyEntry", back_populates="employee")
    payrolls = relationship("Payroll", back_populates="employee")
```

### DailyEntry

The `DailyEntry` table records daily timesheet entries for employees.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the entry       |
| employee_id    | Integer      | FK, Not null      | Reference to the employee             |
| date           | Date         | Not null          | Date of the work                      |
| entry_time     | Time         | Not null          | Time when employee started work       |
| exit_time      | Time         | Not null          | Time when employee ended work         |
| lunch_duration | Integer      | Not null          | Lunch break duration in minutes       |

```python
class DailyEntry(Base):
    __tablename__ = "daily_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    entry_time = Column(Time)
    exit_time = Column(Time)
    lunch_duration = Column(Integer)  # in minutes
    
    employee = relationship("Employee", back_populates="daily_entries")
```

### Payroll

The `Payroll` table stores payroll records for employees.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the payroll     |
| employee_id    | Integer      | FK, Not null      | Reference to the employee             |
| period_start   | Date         | Not null          | Start date of the pay period          |
| period_end     | Date         | Not null          | End date of the pay period            |
| hours_worked   | Numeric(10,2)| Not null          | Total hours worked in the period      |
| amount_paid    | Numeric(10,2)| Not null          | Total amount paid to the employee     |
| payment_method | String(20)   | Not null          | Method of payment                     |

```python
class Payroll(Base):
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    hours_worked = Column(Numeric(10, 2))
    amount_paid = Column(Numeric(10, 2))
    payment_method = Column(String(20))
    
    employee = relationship("Employee", back_populates="payrolls")
```

### Project

The `Project` table stores information about company projects.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the project     |
| name           | String(200)  | Not null          | Project name or description           |
| materials_cost | Numeric(10,2)| Not null          | Cost of materials for the project     |
| labor_cost     | Numeric(10,2)| Not null          | Cost of labor for the project         |
| amount_charged | Numeric(10,2)| Not null          | Amount charged to the client          |

```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    materials_cost = Column(Numeric(10, 2))
    labor_cost = Column(Numeric(10, 2))
    amount_charged = Column(Numeric(10, 2))
    
    invoices = relationship("Invoice", back_populates="project")
```

### Invoice

The `Invoice` table stores invoice information for projects.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the invoice     |
| project_id     | Integer      | FK, Not null      | Reference to the project              |
| invoice_number | String(50)   | Unique, Not null  | Invoice number                        |
| date           | Date         | Not null          | Date of the invoice                   |
| total_amount   | Numeric(10,2)| Not null          | Total amount of the invoice           |
| paid           | Boolean      | Not null          | Whether the invoice has been paid     |

```python
class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    invoice_number = Column(String(50), unique=True)
    date = Column(Date)
    total_amount = Column(Numeric(10, 2))
    paid = Column(Boolean, default=False)
    
    project = relationship("Project", back_populates="invoices")
```

## Database Indexes

The following indexes are created to optimize query performance:

1. **User Indexes**:
   - Primary key index on `id`
   - Unique index on `username`

2. **Employee Indexes**:
   - Primary key index on `id`
   - Index on `name` for search optimization

3. **DailyEntry Indexes**:
   - Primary key index on `id`
   - Index on `employee_id` for foreign key lookups
   - Index on `date` for date-based queries

4. **Payroll Indexes**:
   - Primary key index on `id`
   - Index on `employee_id` for foreign key lookups
   - Index on `period_start` and `period_end` for date range queries

5. **Project Indexes**:
   - Primary key index on `id`
   - Index on `name` for search optimization

6. **Invoice Indexes**:
   - Primary key index on `id`
   - Index on `project_id` for foreign key lookups
   - Unique index on `invoice_number`
   - Index on `date` for date-based queries
   - Index on `paid` for filtering paid/unpaid invoices
   
7. **Supplier Indexes**:
   - Primary key index on `id`
   - Index on `name` for search optimization
   
8. **ExpenseCategory Indexes**:
   - Primary key index on `id`
   - Unique index on `name` for fast category lookups
   
9. **AccountsPayable Indexes**:
   - Primary key index on `id`
   - Index on `supplier_id` for foreign key lookups
   - Index on `category_id` for foreign key lookups
   - Index on `due_date` for date-based queries
   - Index on `status` for status-based filtering
   
10. **AccountsPaid Indexes**:
    - Primary key index on `id`
    - Index on `supplier_id` for foreign key lookups
    - Index on `category_id` for foreign key lookups
    - Index on `payment_date` for date-based queries
    - Index on `payment_method` for payment method filtering
   
11. **MonthlyExpense Indexes**:
    - Primary key index on `id`
    - Index on `category_id` for foreign key lookups
    - Index on `expense_date` for date-based queries
    - Index on `payment_method` for payment method filtering

### Supplier

The `Supplier` table stores information about vendors and service providers.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the supplier    |
| name           | String(100)  | Not null          | Supplier's company name              |
| contact_person | String(100)  | Not null          | Name of primary contact              |
| phone          | String(20)   | Not null          | Contact phone number                 |
| email          | String(100)  | Not null          | Contact email address                |
| address        | String(200)  | Not null          | Physical address                     |

```python
class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    
    accounts_payable = relationship("AccountsPayable", back_populates="supplier")
    accounts_paid = relationship("AccountsPaid", back_populates="supplier")
```

### ExpenseCategory

The `ExpenseCategory` table defines categories for organizing expenses.

| Column      | Type         | Constraints       | Description                           |
|-------------|--------------|-------------------|---------------------------------------|
| id          | Integer      | PK, Auto-increment| Unique identifier for the category    |
| name        | String(50)   | Not null, Unique  | Category name                        |
| description | String(200)  | Not null          | Description of the category          |

```python
class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(200), nullable=False)
    
    accounts_payable = relationship("AccountsPayable", back_populates="category")
    accounts_paid = relationship("AccountsPaid", back_populates="category")
    monthly_expenses = relationship("MonthlyExpense", back_populates="category")
```

### AccountsPayable

The `AccountsPayable` table tracks pending bills and upcoming payments.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the payable    |
| supplier_id    | Integer      | FK, Not null      | Reference to the supplier            |
| category_id    | Integer      | FK, Not null      | Reference to the expense category    |
| description    | String(200)  | Not null          | Description of the payable          |
| amount         | Numeric(10,2)| Not null          | Amount due                          |
| issue_date     | Date         | Not null          | Date the bill was issued            |
| due_date       | Date         | Not null          | Date the payment is due             |
| payment_method | String(50)   | Not null          | Method of payment                   |
| status         | String(20)   | Not null          | Status (pending, paid, overdue)     |
| notes          | String(500)  | Nullable          | Additional notes                    |

```python
class AccountsPayable(Base):
    __tablename__ = "accounts_payable"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    notes = Column(String(500))
    
    supplier = relationship("Supplier", back_populates="accounts_payable")
    category = relationship("ExpenseCategory", back_populates="accounts_payable")
```

### AccountsPaid

The `AccountsPaid` table records completed payments with receipt uploads.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the payment    |
| supplier_id    | Integer      | FK, Not null      | Reference to the supplier            |
| category_id    | Integer      | FK, Not null      | Reference to the expense category    |
| description    | String(200)  | Not null          | Description of the payment          |
| amount         | Numeric(10,2)| Not null          | Amount paid                         |
| payment_date   | Date         | Not null          | Date the payment was made           |
| payment_method | String(50)   | Not null          | Method of payment                   |
| check_number   | String(50)   | Nullable          | Check number if paid by check       |
| bank_name      | String(100)  | Nullable          | Bank name if paid by check          |
| receipt_file   | String(200)  | Nullable          | Path to uploaded receipt file       |
| notes          | String(500)  | Nullable          | Additional notes                    |

```python
class AccountsPaid(Base):
    __tablename__ = "accounts_paid"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    check_number = Column(String(50))
    bank_name = Column(String(100))
    receipt_file = Column(String(200))
    notes = Column(String(500))
    
    supplier = relationship("Supplier", back_populates="accounts_paid")
    category = relationship("ExpenseCategory", back_populates="accounts_paid")
```

### MonthlyExpense

The `MonthlyExpense` table tracks recurring monthly expenses.

| Column         | Type         | Constraints       | Description                           |
|----------------|--------------|-------------------|---------------------------------------|
| id             | Integer      | PK, Auto-increment| Unique identifier for the expense    |
| category_id    | Integer      | FK, Not null      | Reference to the expense category    |
| description    | String(200)  | Not null          | Description of the expense          |
| amount         | Numeric(10,2)| Not null          | Amount of the expense               |
| expense_date   | Date         | Not null          | Date of the expense                 |
| payment_method | String(50)   | Not null          | Method of payment                   |
| notes          | String(500)  | Nullable          | Additional notes                    |

```python
class MonthlyExpense(Base):
    __tablename__ = "monthly_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    expense_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    notes = Column(String(500))
    
    category = relationship("ExpenseCategory", back_populates="monthly_expenses")
```

## Database Constraints

The following constraints are enforced to maintain data integrity:

1. **Primary Key Constraints**:
   - Each table has a primary key constraint on the `id` column

2. **Foreign Key Constraints**:
   - `DailyEntry.employee_id` references `Employee.id`
   - `Payroll.employee_id` references `Employee.id`
   - `Invoice.project_id` references `Project.id`
   - `AccountsPayable.supplier_id` references `Supplier.id`
   - `AccountsPayable.category_id` references `ExpenseCategory.id`
   - `AccountsPaid.supplier_id` references `Supplier.id`
   - `AccountsPaid.category_id` references `ExpenseCategory.id`
   - `MonthlyExpense.category_id` references `ExpenseCategory.id`

3. **Unique Constraints**:
   - `User.username` must be unique
   - `Invoice.invoice_number` must be unique
   - `ExpenseCategory.name` must be unique

4. **Not Null Constraints**:
   - Critical fields in all tables have not null constraints

## Calculated Fields

The system uses several calculated fields that are not stored in the database but are computed at runtime:

1. **Hours Worked**:
   - Calculated from `entry_time`, `exit_time`, and `lunch_duration` in the `DailyEntry` table

2. **Project Profit**:
   - Calculated as `amount_charged - materials_cost - labor_cost` from the `Project` table

3. **Project Profit Margin**:
   - Calculated as `(amount_charged - materials_cost - labor_cost) / amount_charged * 100` from the `Project` table

## Database Migrations

Database migrations are managed using Alembic, which allows for:

1. **Schema Evolution**: Adding, modifying, or removing tables and columns
2. **Data Migration**: Moving data between tables or transforming existing data
3. **Version Control**: Tracking database schema changes over time

## Backup and Recovery

The database backup strategy includes:

1. **Daily Backups**: Full database dumps are created daily
2. **Transaction Logs**: Transaction logs are backed up hourly
3. **Offsite Storage**: Backups are stored both locally and in an offsite location
4. **Retention Policy**: Backups are retained for 30 days

## Data Dictionary

For a complete reference of all database fields, their types, constraints, and descriptions, refer to the [Data Dictionary](data_dictionary.md) document.
