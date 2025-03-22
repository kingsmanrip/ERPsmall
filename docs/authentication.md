# Authentication System

## Overview

The Mauricio Paint and Dry Wall Financial Management System uses a robust authentication system based on JSON Web Tokens (JWT) with cookie-based storage. This document explains how the authentication system works, its components, security features, and best practices.

## Authentication Flow

```
┌─────────────┐      ┌────────────────┐      ┌────────────────┐
│             │      │                │      │                │
│    User     │─────▶│  Login Form    │─────▶│  /token API    │
│             │      │                │      │                │
└─────────────┘      └────────────────┘      └────────────────┘
                                                     │
                                                     ▼
┌─────────────┐      ┌────────────────┐      ┌────────────────┐
│             │      │                │      │                │
│  Protected  │◀─────│  JWT Token     │◀─────│  JWT Creation  │
│  Resources  │      │  in Cookie     │      │                │
│             │      │                │      │                │
└─────────────┘      └────────────────┘      └────────────────┘
```

## Components

### 1. User Authentication (`auth.py`)

The `auth.py` module handles the core authentication functionality:

- Password hashing and verification using bcrypt
- JWT token generation and validation
- User authentication logic

```python
# Key components from auth.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Functions for authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
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
```

### 2. Token Endpoint (`main.py`)

The token endpoint handles login requests and issues JWT tokens:

```python
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set the token as a cookie
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    
    return response
```

### 3. Cookie-Based Authentication

The system supports both header-based and cookie-based authentication:

```python
def get_current_user_from_cookie_or_token(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme_optional)
):
    # First try to get the token from the Authorization header
    if token:
        return get_current_user(token, db)
    
    # If no token in header, try to get it from cookies
    token_cookie = request.cookies.get("access_token")
    if token_cookie and token_cookie.startswith("Bearer "):
        token = token_cookie.split(" ")[1]
        return get_current_user(token, db)
    
    # If no token found, the user is not authenticated
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
```

### 4. Frontend Authentication (`login.html`)

The login page handles user authentication on the client side:

```javascript
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // On successful login, simply redirect to dashboard
            // The cookie will be automatically sent with the request
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            const errorDiv = document.getElementById('loginError');
            errorDiv.textContent = data.detail || 'Login failed. Please check your credentials.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        const errorDiv = document.getElementById('loginError');
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.style.display = 'block';
    }
});
```

## Security Features

### 1. Password Hashing

All user passwords are hashed using bcrypt before being stored in the database. Bcrypt is a secure password hashing algorithm that includes:

- Salt generation and storage
- Configurable work factor to adjust computational complexity
- Protection against rainbow table attacks

### 2. JWT Security

The JWT implementation includes several security features:

- Signed tokens using HMAC-SHA256 (HS256) algorithm
- Expiration time (24 hours by default)
- Token validation on each protected request

### 3. Cookie Security

When using cookie-based authentication, the following security measures are implemented:

- HttpOnly flag to prevent JavaScript access to the cookie
- SameSite policy to prevent CSRF attacks
- Secure flag (in production) to ensure cookies are only sent over HTTPS
- Expiration time matching the JWT token expiration

### 4. CSRF Protection

Cross-Site Request Forgery (CSRF) protection is implemented through:

- SameSite cookie policy
- CSRF tokens for sensitive operations
- Proper validation of request origins

### 5. Rate Limiting

To prevent brute force attacks, the system implements rate limiting on authentication endpoints:

- 5 login attempts per minute per IP address
- Exponential backoff for repeated failed attempts
- IP blocking after multiple consecutive failed attempts

## Authentication Workflows

### 1. User Login

1. User enters username and password in the login form
2. Client sends credentials to the `/token` endpoint
3. Server verifies credentials against the database
4. If valid, server generates a JWT token and sets it as a cookie
5. Client is redirected to the dashboard

### 2. Session Validation

1. Client makes a request to a protected endpoint
2. Server extracts the JWT token from the cookie or Authorization header
3. Server validates the token signature and expiration
4. If valid, server identifies the user and processes the request
5. If invalid, server returns a 401 Unauthorized response

### 3. Session Expiration

1. JWT tokens have a 24-hour expiration by default
2. When a token expires, the user is redirected to the login page
3. User must re-authenticate to obtain a new token

### 4. Logout

1. User clicks the logout button
2. Client sends a request to the `/logout` endpoint
3. Server clears the authentication cookie
4. User is redirected to the login page

## Role-Based Access Control

The system implements role-based access control (RBAC) to restrict access to certain features:

### User Roles

- **Administrator**: Full access to all system features
- **Accountant**: Access to financial modules (payroll, invoices)
- **Project Manager**: Access to project management features
- **Employee**: Limited access to timesheet entry only

### Role Implementation

```python
def role_required(required_role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user_from_cookie_or_token), **kwargs):
            if current_user.role != required_role and current_user.role != "administrator":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation requires {required_role} role"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Example usage
@app.get("/payroll")
@role_required("accountant")
async def get_payroll(current_user: User = Depends(get_current_user_from_cookie_or_token)):
    # Only administrators and accountants can access this endpoint
    return {"message": "Payroll data"}
```

## Best Practices

### 1. Secure Configuration

- Store the JWT secret key as an environment variable
- Use a strong, randomly generated secret key
- Rotate secret keys periodically
- Use HTTPS in production environments

### 2. Token Management

- Set appropriate token expiration times
- Implement token revocation for sensitive operations
- Consider using refresh tokens for long-lived sessions

### 3. Password Policies

- Enforce strong password requirements
- Implement account lockout after failed attempts
- Require periodic password changes for sensitive accounts

### 4. Monitoring and Logging

- Log authentication events (successful logins, failed attempts)
- Monitor for suspicious activity (multiple failed logins)
- Implement alerts for potential security breaches

## Troubleshooting

### Common Issues

1. **"Not authenticated" error**:
   - Check that the token cookie is being set correctly
   - Verify that the token has not expired
   - Ensure the secret key is consistent across server instances

2. **"Could not validate credentials" error**:
   - The JWT token is invalid or has been tampered with
   - The secret key used for validation doesn't match the one used for creation
   - The token has expired

3. **"Operation requires X role" error**:
   - The authenticated user does not have the required role
   - Check user permissions in the database

### Debugging Authentication Issues

1. Check browser cookies to ensure the token is being set
2. Verify token expiration using a JWT debugger
3. Check server logs for authentication errors
4. Test authentication endpoints directly using tools like Postman

## Security Considerations

### 1. Token Storage

- Never store tokens in localStorage (vulnerable to XSS)
- Use HttpOnly cookies for token storage
- Consider using secure, SameSite cookies in production

### 2. HTTPS

- Always use HTTPS in production environments
- Configure proper SSL/TLS settings
- Implement HSTS for additional security

### 3. Regular Security Audits

- Conduct regular security audits of the authentication system
- Stay updated on security best practices
- Apply security patches promptly

## Conclusion

The authentication system for the Mauricio Paint and Dry Wall Financial Management System provides a secure, robust mechanism for user authentication and authorization. By combining JWT tokens with secure cookie storage and role-based access control, the system ensures that only authorized users can access sensitive financial information.
