from models import User
from passlib.context import CryptContext

# Настройки для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хранилище пользователей
users = {}
master_user = User(id=1, username="admin", first_name="admin", last_name="admin", email="admin@example.com", hashed_password=pwd_context.hash("secret"))
users[1] = master_user
