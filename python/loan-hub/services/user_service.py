import bcrypt
from sqlalchemy.orm import Session
from models.db_models import User
from models.schemas import UserCreate, UserLogin
from models.enums import UserRole
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from exceptions.custom_exceptions import DuplicateUserError, InvalidCredentialsError, UserNotFoundError
from decorators.timer import timer

class UserService:
    def __init__(self, db: Session):
        self.repo = SQLAlchemyRepository(db, User)
        self.db = db

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @timer
    def register_user(self, user_data: UserCreate) -> User:
        # Check for existing user
        if self.db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first():
            raise DuplicateUserError()
        
        hashed_pw = self._hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_pw,
            phone=user_data.phone,
            monthly_income=user_data.monthly_income,
            role=UserRole.USER
        )
        return self.repo.add(new_user)

    @timer
    def login(self, login_data: UserLogin) -> User:
        user = self.db.query(User).filter(User.username == login_data.username).first()
        if not user or not self._verify_password(login_data.password, user.password):
            raise InvalidCredentialsError()
        return user

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def get_user_by_username(self, username: str) -> User:
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise UserNotFoundError(f"User {username} not found")
        return user
