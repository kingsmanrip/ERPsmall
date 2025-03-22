from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import User, Employee, Project
from passlib.context import CryptContext
from decimal import Decimal

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

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
