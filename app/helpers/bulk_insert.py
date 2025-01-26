from faker import Faker
import os
import logging
import sys
import time

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import (User, Companies, DirectMessages, Jobs, Notifications)


# Database connection based on environment
host = os.environ.get('DB_HOST', 'localhost')

# Database connection
engine = create_engine("mysql+pymysql://root:RrushKumbullaQepe%4030@localhost:3307/mydb")
Session = sessionmaker(bind=engine)

# Initialize Faker for generating random data
fake = Faker()
db = Session()

def insert_companies(n=10):
    try:
        for _ in range(n):
            company = Companies(
                id=fake.random_int(min=1, max=1000),
                email=fake.email(),
                name=fake.company(),
                password=fake.password(),
                description=fake.text(),
                location=fake.city()
            )
            db.add(company)
        db.commit()
        print(f"Successfully inserted {n} companies")
    except Exception as e:
        print(f"Error inserting companies: {e}")
        db.rollback()


def insert_jobs(n=100):
    try:
        # Get all company IDs
        company_ids = [company.id for company in db.query(Companies).all()]
        if not company_ids:
            print("No companies found in database. Cannot insert jobs.")
            return
        
        for _ in range(n):
            job = Jobs(
                # Ensure unique job id
                id=fake.unique.random_int(min=1, max=1000000),
                title=fake.job(),
                description=fake.text(),
                location=fake.city(),
                salary=fake.random_int(min=1000, max=10000),
                company_id=fake.random_element(elements=company_ids)
            )
            db.add(job)
        db.commit()
        print(f"Successfully inserted {n} jobs")
    except Exception as e:
        print(f"Error inserting jobs: {e}")
        db.rollback()


def get_all_companies():
    try:
        # Execute query within a session
        with Session() as session:
            companies = session.query(Companies).all()
            if not companies:
                print("No companies found in database")
                return []
            
            print(f"Found {len(companies)} companies:")
            for company in companies:
                print(f"ID: {company.id}, "
                      f"Name: {company.name}, "
                      f"Password: {company.password}, "
                      f"Email: {company.email}, "
                      f"Location: {company.location}")
            return companies
            
    except Exception as e:
        print(f"Error querying companies: {e}")
        return []
    

def testing_world_db():
    try:
        # SELECT j.* FROM jobs j INNER JOIN companies c ON c.id = j.company_id -- where email='company1@test.com'
        query = "SELECT * from companies"
        with engine.connect() as connection:
            result = connection.execute(text(query))
            for row in result:
                print(row)
            
    except Exception as e:
        print(f"Error querying companies: {e}")
        return []

if __name__ == "__main__":
    # Insert companies
    # insert_companies(10)
    # time.sleep(2)
    # Get all companies
    # get_all_companies()
    # insert_jobs(100)
    testing_world_db()