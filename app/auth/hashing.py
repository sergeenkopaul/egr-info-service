import os

from passlib.context import CryptContext

#Provide in production environmental variable!
#You can get secret key just by running in terminal
#command "openssl rand -hex 32"

SECRET_KEY = os.environ.get("SECRET_KEY", "2b1de5287cca50a98b5f2ea9ff9cca67ee00297b51b616f1415b2ca312ec4e95") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
