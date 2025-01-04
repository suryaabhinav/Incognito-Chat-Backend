import os
from dotenv import load_dotenv

load_dotenv()

# Load secret key from environment or .env file
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
