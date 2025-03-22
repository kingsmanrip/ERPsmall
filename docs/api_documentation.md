# API Documentation

## Overview

The Mauricio Paint and Dry Wall Financial Management System provides a RESTful API that allows for programmatic interaction with the system. This document outlines the available endpoints, request/response formats, authentication requirements, and example usage.

## Base URL

All API endpoints are relative to the base URL of your installation:

```
http://your-domain.com/api/v1
```

For local development:

```
http://localhost:8000/api/v1
```

## Authentication

### JWT Authentication

The API uses JSON Web Tokens (JWT) for authentication. To authenticate, you need to:

1. Obtain a token by sending a POST request to the `/token` endpoint with valid credentials
2. Include the token in the `Authorization` header of subsequent requests

#### Obtaining a Token

**Request:**

```http
POST /token HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=Patricia&password=pati2025
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Using the Token

Include the token in the `Authorization` header:

```http
GET /api/v1/employees HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Cookie Authentication

For web applications, the system also supports cookie-based authentication. When a user logs in through the web interface, the token is stored in a secure HTTP-only cookie that is automatically included in subsequent requests.

## API Endpoints

### Employees

#### List All Employees

```http
GET /api/v1/employees
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "hourly_rate": 20.0
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "hourly_rate": 22.0
  }
]
```

#### Get Employee by ID

```http
GET /api/v1/employees/{employee_id}
```

**Response:**

```json
{
  "id": 1,
  "name": "John Doe",
  "hourly_rate": 20.0
}
```

#### Create Employee

```http
POST /api/v1/employees
Content-Type: application/json

{
  "name": "Mike Johnson",
  "hourly_rate": 25.0
}
```

**Response:**

```json
{
  "id": 3,
  "name": "Mike Johnson",
  "hourly_rate": 25.0
}
```

#### Update Employee

```http
PUT /api/v1/employees/{employee_id}
Content-Type: application/json

{
  "name": "Michael Johnson",
  "hourly_rate": 26.0
}
```

**Response:**

```json
{
  "id": 3,
  "name": "Michael Johnson",
  "hourly_rate": 26.0
}
```

#### Delete Employee

```http
DELETE /api/v1/employees/{employee_id}
```

**Response:**

```json
{
  "message": "Employee deleted successfully"
}
```

### Daily Entries

#### List Daily Entries

```http
GET /api/v1/daily-entries
```

**Query Parameters:**

- `employee_id` (optional): Filter by employee ID
- `start_date` (optional): Filter entries on or after this date (YYYY-MM-DD)
- `end_date` (optional): Filter entries on or before this date (YYYY-MM-DD)

**Response:**

```json
[
  {
    "id": 1,
    "employee_id": 1,
    "date": "2025-03-15",
    "entry_time": "08:00:00",
    "exit_time": "17:00:00",
    "lunch_duration": 60
  },
  {
    "id": 2,
    "employee_id": 1,
    "date": "2025-03-16",
    "entry_time": "08:30:00",
    "exit_time": "16:30:00",
    "lunch_duration": 45
  }
]
```

#### Create Daily Entry

```http
POST /api/v1/daily-entries
Content-Type: application/json

{
  "employee_id": 1,
  "date": "2025-03-17",
  "entry_time": "08:15:00",
  "exit_time": "17:15:00",
  "lunch_duration": 60
}
```

**Response:**

```json
{
  "id": 3,
  "employee_id": 1,
  "date": "2025-03-17",
  "entry_time": "08:15:00",
  "exit_time": "17:15:00",
  "lunch_duration": 60
}
```

### Projects

#### List All Projects

```http
GET /api/v1/projects
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Residential Painting - 123 Main St",
    "materials_cost": 1500.0,
    "labor_cost": 2500.0,
    "amount_charged": 5000.0,
    "profit": 1000.0,
    "profit_margin": 20.0
  },
  {
    "id": 2,
    "name": "Commercial Drywall - Office Building",
    "materials_cost": 3000.0,
    "labor_cost": 4500.0,
    "amount_charged": 9000.0,
    "profit": 1500.0,
    "profit_margin": 16.67
  }
]
```

#### Create Project

```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "Residential Drywall - 456 Oak St",
  "materials_cost": 2000.0,
  "labor_cost": 3000.0,
  "amount_charged": 6500.0
}
```

**Response:**

```json
{
  "id": 3,
  "name": "Residential Drywall - 456 Oak St",
  "materials_cost": 2000.0,
  "labor_cost": 3000.0,
  "amount_charged": 6500.0,
  "profit": 1500.0,
  "profit_margin": 23.08
}
```

### Payroll

#### List Payroll Entries

```http
GET /api/v1/payroll
```

**Query Parameters:**

- `employee_id` (optional): Filter by employee ID
- `start_date` (optional): Filter entries on or after this date (YYYY-MM-DD)
- `end_date` (optional): Filter entries on or before this date (YYYY-MM-DD)

**Response:**

```json
[
  {
    "id": 1,
    "employee_id": 1,
    "employee_name": "John Doe",
    "period_start": "2025-03-01",
    "period_end": "2025-03-15",
    "hours_worked": 80.0,
    "amount_paid": 1600.0,
    "payment_method": "Direct Deposit"
  },
  {
    "id": 2,
    "employee_id": 2,
    "employee_name": "Jane Smith",
    "period_start": "2025-03-01",
    "period_end": "2025-03-15",
    "hours_worked": 75.0,
    "amount_paid": 1650.0,
    "payment_method": "Check"
  }
]
```

#### Create Payroll Entry

```http
POST /api/v1/payroll
Content-Type: application/json

{
  "employee_id": 1,
  "period_start": "2025-03-16",
  "period_end": "2025-03-31",
  "hours_worked": 85.0,
  "amount_paid": 1700.0,
  "payment_method": "Direct Deposit"
}
```

**Response:**

```json
{
  "id": 3,
  "employee_id": 1,
  "employee_name": "John Doe",
  "period_start": "2025-03-16",
  "period_end": "2025-03-31",
  "hours_worked": 85.0,
  "amount_paid": 1700.0,
  "payment_method": "Direct Deposit"
}
```

### Invoices

#### List Invoices

```http
GET /api/v1/invoices
```

**Query Parameters:**

- `project_id` (optional): Filter by project ID
- `paid` (optional): Filter by payment status (true/false)

**Response:**

```json
[
  {
    "id": 1,
    "project_id": 1,
    "project_name": "Residential Painting - 123 Main St",
    "invoice_number": "INV-2025-001",
    "date": "2025-03-20",
    "total_amount": 5000.0,
    "paid": true
  },
  {
    "id": 2,
    "project_id": 2,
    "project_name": "Commercial Drywall - Office Building",
    "invoice_number": "INV-2025-002",
    "date": "2025-03-22",
    "total_amount": 9000.0,
    "paid": false
  }
]
```

#### Create Invoice

```http
POST /api/v1/invoices
Content-Type: application/json

{
  "project_id": 3,
  "invoice_number": "INV-2025-003",
  "date": "2025-03-25",
  "total_amount": 6500.0,
  "paid": false
}
```

**Response:**

```json
{
  "id": 3,
  "project_id": 3,
  "project_name": "Residential Drywall - 456 Oak St",
  "invoice_number": "INV-2025-003",
  "date": "2025-03-25",
  "total_amount": 6500.0,
  "paid": false
}
```

#### Generate Invoice PDF

```http
GET /api/v1/invoices/{invoice_id}/pdf
```

**Response:**

The response will be a PDF file with the appropriate Content-Type header.

#### Mark Invoice as Paid

```http
PUT /api/v1/invoices/{invoice_id}/paid
```

**Response:**

```json
{
  "id": 3,
  "project_id": 3,
  "project_name": "Residential Drywall - 456 Oak St",
  "invoice_number": "INV-2025-003",
  "date": "2025-03-25",
  "total_amount": 6500.0,
  "paid": true
}
```

### Reports

#### Payroll Summary Report

```http
GET /api/v1/reports/payroll-summary
```

**Query Parameters:**

- `start_date` (required): Start date for the report (YYYY-MM-DD)
- `end_date` (required): End date for the report (YYYY-MM-DD)

**Response:**

```json
{
  "report_name": "Payroll Summary",
  "start_date": "2025-03-01",
  "end_date": "2025-03-31",
  "total_amount_paid": 4950.0,
  "total_hours_worked": 240.0,
  "employees": [
    {
      "employee_id": 1,
      "employee_name": "John Doe",
      "hours_worked": 165.0,
      "amount_paid": 3300.0
    },
    {
      "employee_id": 2,
      "employee_name": "Jane Smith",
      "hours_worked": 75.0,
      "amount_paid": 1650.0
    }
  ]
}
```

#### Project Profitability Report

```http
GET /api/v1/reports/project-profitability
```

**Response:**

```json
{
  "report_name": "Project Profitability",
  "total_projects": 3,
  "total_revenue": 20500.0,
  "total_costs": 16500.0,
  "total_profit": 4000.0,
  "average_profit_margin": 19.51,
  "projects": [
    {
      "project_id": 1,
      "project_name": "Residential Painting - 123 Main St",
      "materials_cost": 1500.0,
      "labor_cost": 2500.0,
      "amount_charged": 5000.0,
      "profit": 1000.0,
      "profit_margin": 20.0
    },
    {
      "project_id": 2,
      "project_name": "Commercial Drywall - Office Building",
      "materials_cost": 3000.0,
      "labor_cost": 4500.0,
      "amount_charged": 9000.0,
      "profit": 1500.0,
      "profit_margin": 16.67
    },
    {
      "project_id": 3,
      "project_name": "Residential Drywall - 456 Oak St",
      "materials_cost": 2000.0,
      "labor_cost": 3000.0,
      "amount_charged": 6500.0,
      "profit": 1500.0,
      "profit_margin": 23.08
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `201 Created`: A new resource was created successfully
- `400 Bad Request`: The request was invalid or cannot be served
- `401 Unauthorized`: Authentication is required or failed
- `403 Forbidden`: The authenticated user does not have permission
- `404 Not Found`: The requested resource does not exist
- `500 Internal Server Error`: An error occurred on the server

Error responses include a JSON body with details:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

To ensure system stability, the API implements rate limiting:

- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

When the rate limit is exceeded, the API returns a `429 Too Many Requests` status code.

## Pagination

For endpoints that return lists of items, the API supports pagination:

**Request:**

```http
GET /api/v1/employees?skip=0&limit=10
```

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "hourly_rate": 20.0
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "hourly_rate": 22.0
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 10
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

**Filtering:**

```http
GET /api/v1/payroll?employee_id=1&payment_method=Direct%20Deposit
```

**Sorting:**

```http
GET /api/v1/projects?sort=profit_margin&order=desc
```

## Versioning

The API uses URL versioning to ensure backward compatibility. The current version is `v1`.

## Webhooks

The system supports webhooks for event notifications. You can register webhook URLs to receive notifications for events such as:

- New invoice created
- Invoice paid
- Payroll processed

To register a webhook:

```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["invoice.created", "invoice.paid", "payroll.processed"],
  "secret": "your_webhook_secret"
}
```

## API Client Libraries

We provide client libraries for easy integration:

- [Python Client](https://github.com/mauricio-paint-drywall/python-client)
- [JavaScript Client](https://github.com/mauricio-paint-drywall/js-client)

## Example Use Cases

### Calculate Weekly Payroll

```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8000/token",
    data={"username": "Patricia", "password": "pati2025"}
)
token = response.json()["access_token"]

# Get daily entries for the week
start_date = "2025-03-15"
end_date = "2025-03-21"
headers = {"Authorization": f"Bearer {token}"}

entries = requests.get(
    f"http://localhost:8000/api/v1/daily-entries?start_date={start_date}&end_date={end_date}",
    headers=headers
).json()

# Calculate hours worked per employee
employee_hours = {}
for entry in entries:
    employee_id = entry["employee_id"]
    
    # Calculate hours worked for this entry
    entry_time = entry["entry_time"]
    exit_time = entry["exit_time"]
    lunch_duration = entry["lunch_duration"]
    
    # Convert times to hours
    entry_hour, entry_minute = map(int, entry_time.split(":")[:2])
    exit_hour, exit_minute = map(int, exit_time.split(":")[:2])
    
    entry_decimal = entry_hour + entry_minute / 60
    exit_decimal = exit_hour + exit_minute / 60
    
    hours_worked = exit_decimal - entry_decimal - (lunch_duration / 60)
    
    if employee_id not in employee_hours:
        employee_hours[employee_id] = 0
    
    employee_hours[employee_id] += hours_worked

# Create payroll entries
for employee_id, hours in employee_hours.items():
    # Get employee details
    employee = requests.get(
        f"http://localhost:8000/api/v1/employees/{employee_id}",
        headers=headers
    ).json()
    
    # Calculate amount to pay
    amount_paid = hours * employee["hourly_rate"]
    
    # Create payroll entry
    payroll_data = {
        "employee_id": employee_id,
        "period_start": start_date,
        "period_end": end_date,
        "hours_worked": hours,
        "amount_paid": amount_paid,
        "payment_method": "Direct Deposit"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/payroll",
        json=payroll_data,
        headers=headers
    )
    
    print(f"Created payroll entry for {employee['name']}: {response.json()}")
```

### Generate Monthly Project Profitability Report

```javascript
// Example using the JavaScript client library
const MauricioClient = require('@mauricio-paint-drywall/js-client');

async function generateMonthlyReport() {
  // Initialize client
  const client = new MauricioClient({
    baseUrl: 'http://localhost:8000',
    username: 'Patricia',
    password: 'pati2025'
  });
  
  // Authenticate
  await client.authenticate();
  
  // Get project profitability report
  const report = await client.reports.getProjectProfitability();
  
  // Format and display the report
  console.log('=== PROJECT PROFITABILITY REPORT ===');
  console.log(`Total Projects: ${report.total_projects}`);
  console.log(`Total Revenue: $${report.total_revenue.toFixed(2)}`);
  console.log(`Total Costs: $${report.total_costs.toFixed(2)}`);
  console.log(`Total Profit: $${report.total_profit.toFixed(2)}`);
  console.log(`Average Profit Margin: ${report.average_profit_margin.toFixed(2)}%`);
  console.log('\nProject Details:');
  
  // Sort projects by profit margin (highest first)
  const sortedProjects = report.projects.sort((a, b) => b.profit_margin - a.profit_margin);
  
  sortedProjects.forEach(project => {
    console.log(`\n${project.project_name}`);
    console.log(`  Materials Cost: $${project.materials_cost.toFixed(2)}`);
    console.log(`  Labor Cost: $${project.labor_cost.toFixed(2)}`);
    console.log(`  Amount Charged: $${project.amount_charged.toFixed(2)}`);
    console.log(`  Profit: $${project.profit.toFixed(2)}`);
    console.log(`  Profit Margin: ${project.profit_margin.toFixed(2)}%`);
  });
}

generateMonthlyReport().catch(console.error);
```

## API Changes and Deprecation Policy

We follow semantic versioning for the API. Breaking changes will only be introduced in major version updates, with at least 6 months of overlap support for the previous version.

When an endpoint or feature is deprecated:

1. It will be marked as deprecated in the documentation
2. A deprecation warning will be included in the response headers
3. It will continue to function for at least 6 months
4. A migration path to the new endpoint or feature will be provided

## Support and Feedback

For API support or to provide feedback:

- Email: api-support@mauricio-paint-drywall.com
- API Issue Tracker: https://github.com/mauricio-paint-drywall/api/issues
