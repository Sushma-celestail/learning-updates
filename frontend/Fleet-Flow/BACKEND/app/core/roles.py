from enum import Enum

class Role(str, Enum):
    ADMIN   = "Admin"
    MANAGER = "Manager"
    CLERK   = "Clerk"
    DRIVER  = "Driver"