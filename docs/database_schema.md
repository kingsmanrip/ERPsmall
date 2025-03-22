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

## Database Constraints

The following constraints are enforced to maintain data integrity:

1. **Primary Key Constraints**:
   - Each table has a primary key constraint on the `id` column

2. **Foreign Key Constraints**:
   - `DailyEntry.employee_id` references `Employee.id`
   - `Payroll.employee_id` references `Employee.id`
   - `Invoice.project_id` references `Project.id`

3. **Unique Constraints**:
   - `User.username` must be unique
   - `Invoice.invoice_number` must be unique

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
