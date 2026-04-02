## custome exception handling

class Slarytoolowerror(Exception):
    pass

def check_salary(salary):
    if salary < 10000:
        raise Slarytoolowerror("Salary too low")
    return "salary accepted"
salary1=100009
try:
    print(check_salary(salary1))
except Slarytoolowerror as e:
    print(e)

class Salarytoollowerror(Exception):
    pass
def check(salary):
    if salary < 10000:
        raise Salarytoollowerror("salary too low")
    return "salary accepted"
salary1=12000
try:
    print(check(salary1))
except Salarytoollowerror:
    print(salary1)
