from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class LoanPurpose(str, Enum):
    PERSONAL = "personal"
    EDUCATION = "education"
    HOME = "home"
    VEHICLE = "vehicle"
    BUSINESS = "business"

class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"

class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
