# Installation and Setup Guide

## System Requirements

- Python 3.9 or higher
- PostgreSQL 12+ (for production) or SQLite (for development)
- 2GB RAM minimum (4GB recommended)
- 1GB free disk space
- Modern web browser (Chrome, Firefox, Edge, Safari)

## Development Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mauricio-paint-drywall/financial-system.git
cd financial-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**On Linux/macOS:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Database

For development, the system uses SQLite by default. The database configuration is in `database.py`.

If you want to use PostgreSQL for development:

1. Create a PostgreSQL database:
```bash
createdb mauricio_db
```

2. Update the `database.py` file:
```python
DATABASE_URL = "postgresql://username:password@localhost/mauricio_db"
```

### 6. Initialize the Database

```bash
python init_db.py
```

This will create the necessary tables and add sample data including:
- Default user (username: Patricia, password: pati2025)
- Sample employees
- Sample projects

### 7. Run the Development Server

```bash
uvicorn main:app --reload
```

The application will be available at http://127.0.0.1:8000

## Production Deployment

### 1. Server Requirements

- Ubuntu 20.04 LTS or newer
- PostgreSQL 12+
- Nginx
- Supervisor (for process management)
- SSL certificate (for HTTPS)

### 2. Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx supervisor
```

### 3. Create a PostgreSQL Database

```bash
sudo -u postgres psql
postgres=# CREATE DATABASE mauricio_db;
postgres=# CREATE USER mauricio_user WITH PASSWORD 'secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE mauricio_db TO mauricio_user;
postgres=# \q
```

### 4. Clone the Repository

```bash
git clone https://github.com/mauricio-paint-drywall/financial-system.git
cd financial-system
```

### 5. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 6. Configure the Database for Production

Edit `database.py`:

```python
DATABASE_URL = "postgresql://mauricio_user:secure_password@localhost/mauricio_db"
```

### 7. Initialize the Database

```bash
python init_db.py
```

### 8. Configure Supervisor

Create a new Supervisor configuration file:

```bash
sudo nano /etc/supervisor/conf.d/mauricio.conf
```

Add the following configuration:

```ini
[program:mauricio]
command=/path/to/financial-system/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
directory=/path/to/financial-system
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/mauricio/err.log
stdout_logfile=/var/log/mauricio/out.log
```

Create log directories:

```bash
sudo mkdir -p /var/log/mauricio
sudo chown www-data:www-data /var/log/mauricio
```

### 9. Configure Nginx

Create a new Nginx site configuration:

```bash
sudo nano /etc/nginx/sites-available/mauricio
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/financial-system/static/;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/mauricio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Set Up SSL with Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 11. Start the Application

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mauricio
```

## Security Considerations

1. **Change Default Credentials**: Immediately change the default user password after installation.

2. **Database Security**: 
   - Use a strong password for the database user
   - Restrict database access to localhost only
   - Regularly backup the database

3. **Environment Variables**: Store sensitive information like database credentials and secret keys as environment variables.

4. **Firewall Configuration**: Configure a firewall to only allow necessary ports (80, 443, SSH).

5. **Regular Updates**: Keep the system and all dependencies up to date with security patches.

## Backup and Restore

### Database Backup

```bash
# For PostgreSQL
pg_dump -U mauricio_user -d mauricio_db > backup.sql

# For SQLite
cp mauricio.db mauricio.db.backup
```

### Database Restore

```bash
# For PostgreSQL
psql -U mauricio_user -d mauricio_db < backup.sql

# For SQLite
cp mauricio.db.backup mauricio.db
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check database credentials
   - Ensure PostgreSQL service is running
   - Verify network connectivity to the database server

2. **Permission Issues**:
   - Check file permissions for log directories
   - Ensure the application has write access to necessary directories

3. **Web Server Issues**:
   - Verify Nginx configuration
   - Check Nginx and Supervisor logs
   - Ensure the application is running with `supervisorctl status mauricio`

### Logs

- Application logs: `/var/log/mauricio/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

## Updating the Application

1. Pull the latest changes:
```bash
cd /path/to/financial-system
git pull
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install any new dependencies:
```bash
pip install -r requirements.txt
```

4. Restart the application:
```bash
sudo supervisorctl restart mauricio
```
