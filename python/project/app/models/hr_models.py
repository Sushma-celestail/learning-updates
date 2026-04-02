from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.db.hr_db import BaseHR

class Employee(BaseHR):
    __tablename__ = "employees"
    __table_args__ = {"schema": "HR_DB"}
    employee_id = Column(Integer, primary_key=True)
    join_date = Column(Date)
    employee_name = Column(String)

class Department(BaseHR):
    __tablename__ = "departments"
    __table_args__ = {"schema": "HR_DB"}
    dept_id = Column(Integer, primary_key=True)
    dept_date = Column(Date)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))

class Salary(BaseHR):
    __tablename__ = "salaries"
    __table_args__ = {"schema": "HR_DB"}
    salary_id = Column(Integer, primary_key=True)
    salary_date = Column(Date)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"))