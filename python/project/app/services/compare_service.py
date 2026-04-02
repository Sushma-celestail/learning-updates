from app.models.hr_models import Employee, Department, Salary
from app.models.sales_models import Customer, Order, Payment
from app.core.logger import get_logger

logger = get_logger(__name__)


#  1. HR TABLE COMPARISON
def compare_hr_tables(db):
    logger.info("Starting HR comparison")

    result = []

    employees = db.query(Employee).all()

    for emp in employees:
        dept = db.query(Department).filter_by(employee_id=emp.employee_id).first()
        sal = db.query(Salary).filter_by(employee_id=emp.employee_id).first()

        if (
            not dept or not sal or
            emp.join_date != dept.dept_date or
            emp.join_date != sal.salary_date
        ):
            result.append({
                "employee_id": emp.employee_id,
                "status": "not matched"
            })

    return result


#  2. HR vs SALES COMPARISON
def compare_hr_sales(hr_db, sales_db):
    logger.info("Starting HR vs Sales comparison")

    report = {}

    # Employees vs Customers
    emp = hr_db.query(Employee).all()
    cust = sales_db.query(Customer).all()

    emp_map = {e.employee_id: e.join_date for e in emp}
    cust_map = {c.customer_id: c.created_date for c in cust}

    report["employees_vs_customers"] = [
        {
            "id": k,
            "status": "matched" if emp_map.get(k) == cust_map.get(k) else "not matched"
        }
        for k in set(emp_map) | set(cust_map)
    ]

    # Departments vs Orders
    dept = hr_db.query(Department).all()
    orders = sales_db.query(Order).all()

    dept_map = {d.employee_id: d.dept_date for d in dept}
    order_map = {o.customer_id: o.order_date for o in orders}

    report["departments_vs_orders"] = [
        {
            "id": k,
            "status": "matched" if dept_map.get(k) == order_map.get(k) else "not matched"
        }
        for k in set(dept_map) | set(order_map)
    ]

    # Salaries vs Payments
    sal = hr_db.query(Salary).all()
    pay = sales_db.query(Payment).all()

    sal_map = {s.employee_id: s.salary_date for s in sal}
    pay_map = {p.order_id: p.payment_date for p in pay}

    report["salaries_vs_payments"] = [
        {
            "id": k,
            "status": "matched" if sal_map.get(k) == pay_map.get(k) else "not matched"
        }
        for k in set(sal_map) | set(pay_map)
    ]

    return report

def employee_data(db):
    logger.info("Starting HR comparison")
    employees = db.query(Employee).all()
    return employees

