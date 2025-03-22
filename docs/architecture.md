# System Architecture

## Overview

The Mauricio Paint and Dry Wall Financial Management System is built using a modern web application architecture that emphasizes maintainability, scalability, and security. The system follows a layered architecture pattern with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Presentation   │────▶│    Business     │────▶│     Data        │
│     Layer       │     │     Layer       │     │     Layer       │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│     HTML/CSS    │     │    FastAPI      │     │   SQLAlchemy    │
│   JavaScript    │     │    Endpoints    │     │      ORM        │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │                 │
                                               │   SQLite/       │
                                               │   PostgreSQL    │
                                               │                 │
                                               └─────────────────┘
```

## Component Description

### Presentation Layer
- **Templates**: Jinja2 templates for HTML rendering
- **Static Assets**: CSS, JavaScript, and images
- **Client-Side Logic**: Form validation and interactive UI elements

### Business Layer
- **API Endpoints**: FastAPI routes that handle HTTP requests
- **Authentication**: JWT-based authentication system
- **Business Logic**: Data processing, calculations, and workflow management

### Data Layer
- **ORM**: SQLAlchemy for database interaction
- **Models**: Python classes that represent database tables
- **Database**: SQLite (development) or PostgreSQL (production)

## Key Components

### 1. FastAPI Application (`main.py`)
The core of the application that defines all routes, middleware, and application configuration. It handles HTTP requests, authentication, and coordinates between the presentation and data layers.

### 2. Database Configuration (`database.py`)
Manages database connections, session creation, and provides the foundation for the ORM. It defines the database URL, engine creation, and session management.

### 3. Data Models (`models.py`)
Defines the SQLAlchemy models that represent the database tables. These models include:
- User
- Employee
- DailyEntry
- Payroll
- Project
- Invoice

### 4. Authentication System (`auth.py`)
Handles user authentication, JWT token generation, and verification. It provides security for the application by ensuring only authorized users can access protected resources.

### 5. Templates (`templates/`)
Contains Jinja2 templates for rendering HTML pages. The templates include:
- Login page
- Dashboard
- Timesheet entry
- Project management
- Invoice management
- Payroll management

### 6. Static Assets (`static/`)
Contains CSS, JavaScript, and image files for the frontend. These assets provide styling, interactivity, and visual elements for the user interface.

## Data Flow

1. **User Authentication**:
   - User submits credentials via the login form
   - Server validates credentials and issues a JWT token
   - Token is stored as a cookie for subsequent requests

2. **Timesheet Entry**:
   - User enters employee hours via the timesheet form
   - Server validates and stores the data in the DailyEntry table
   - Hours are used for payroll calculations

3. **Project Management**:
   - User creates or updates project information
   - Server stores project data including costs and charges
   - Project data is used for invoicing and financial reporting

4. **Invoice Generation**:
   - User creates an invoice for a specific project
   - Server generates a PDF invoice using WeasyPrint
   - Invoice is stored in the database and available for download

5. **Payroll Processing**:
   - User processes payroll for employees
   - Server calculates amounts based on hours worked and rates
   - Payroll records are stored with payment method information

## Security Considerations

1. **Authentication**: JWT-based authentication with secure cookie storage
2. **Password Hashing**: Passwords are hashed using bcrypt
3. **CSRF Protection**: Forms include CSRF protection
4. **Input Validation**: All user inputs are validated before processing
5. **Error Handling**: Proper error handling to prevent information leakage

## Scalability

The system is designed to scale in the following ways:

1. **Database Scaling**: Can switch from SQLite to PostgreSQL for production use
2. **Horizontal Scaling**: FastAPI application can be deployed across multiple servers
3. **Caching**: Implements caching for frequently accessed data
4. **Asynchronous Processing**: Uses FastAPI's asynchronous capabilities for improved performance

## Integration Points

The system is designed with the following integration points:

1. **PDF Generation**: WeasyPrint for generating invoice PDFs
2. **Email Notifications**: Can be extended to send email notifications
3. **External APIs**: Structure allows for integration with external services
4. **Data Export**: Capability to export data in various formats

## Development and Deployment

The system follows a development workflow that includes:

1. **Local Development**: Using SQLite for simplified setup
2. **Testing**: Unit and integration tests for key components
3. **Production Deployment**: Using PostgreSQL and proper security configurations
4. **Monitoring**: Logging and error tracking for production environments
