# Mauricio Paint and Dry Wall Financial Management System

## Overview

This financial management system is designed specifically for Mauricio Paint and Dry Wall to handle payroll, project management, invoicing, and financial tracking. The system provides a comprehensive solution for managing the company's financial operations with a focus on:

1. **Payroll Management**: Track employee hours, lunch breaks, and process payroll with different payment methods
2. **Project Management**: Monitor project costs, labor, materials, and calculate profit margins
3. **Financial Tracking**: Generate invoices, track payments, and view financial reports

## Table of Contents

- [System Architecture](docs/architecture.md)
- [Installation and Setup](docs/installation.md)
- [User Guide](docs/user_guide.md)
- [Database Schema](docs/database_schema.md)
- [API Documentation](docs/api_documentation.md)
- [Authentication System](docs/authentication.md)

## Key Features

### Payroll Management
- Weekly timesheet entry with lunch break tracking
- Employee management with customizable hourly rates
- Payroll processing with multiple payment methods
- Automatic calculation of hours worked and amounts due

### Project Management
- Project creation and tracking
- Materials and labor cost tracking
- Profit margin calculation
- Project status monitoring

### Financial Management
- Invoice generation with PDF export
- Comprehensive supplier management
- Expense categorization and tracking
- Accounts payable and accounts paid management
- Monthly expense tracking with payment method details
- Financial reports with data visualization
- Payment forecast and cash flow analysis
- Receipt upload and storage for payments

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **PDF Generation**: WeasyPrint
- **ORM**: SQLAlchemy

## Getting Started

See the [Installation and Setup](docs/installation.md) guide to get started with the system.

## Screenshots

![Dashboard](docs/images/dashboard.png)
![Timesheet Entry](docs/images/timesheet.png)
![Invoice Generation](docs/images/invoice.png)

## License

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

© 2025 Mauricio Paint and Dry Wall
