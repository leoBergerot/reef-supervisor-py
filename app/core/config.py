import os
from dotenv import load_dotenv
#load env file
load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()