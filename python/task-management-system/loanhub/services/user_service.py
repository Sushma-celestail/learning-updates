from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..repositories.sqlalchemy_repository import SQLAlchemyRepository
from ..models.db_models import User
from ..models.schemas import UserCreate, UserLogin
from ..models.enums import UserRole
from ..exceptions.custom_exceptions import DuplicateUserError, InvalidCredentialsError
from ..decorators.timer import timer

# Constants for JWT (referenced in require_role)
SECRET_KEY = "loan-hub-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.repo = SQLAlchemyRepository(db)

    def _get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def _create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @timer
    def register_user(self, user_in: UserCreate) -> User:
        # Check if username or email exists
        if self.repo.find_all(User, username=user_in.username):
            raise DuplicateUserError("Username already taken")
        if self.repo.find_all(User, email=user_in.email):
            raise DuplicateUserError("Email already registered")

        # Create user object
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            password=self._get_password_hash(user_in.password),
            phone=user_in.phone,
            monthly_income=user_in.monthly_income,
            role=UserRole.USER
        )
        return self.repo.save(new_user)

    @timer
    def authenticate_user(self, login_in: UserLogin):
        users = self.repo.find_all(User, username=login_in.username)
        if not users or not self._verify_password(login_in.password, users[0].password):
            raise InvalidCredentialsError()
        
        user = users[0]
        token = self._create_access_token({"sub": user.username, "role": user.role.value})
        
        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }

    def get_user_by_username(self, username: str) -> User:
        users = self.repo.find_all(User, username=username)
        return users[0] if users else None
