import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "5"))
WINDOW_SECONDS = int(os.getenv("WINDOW_SECONDS", "10"))

TOKEN_BUCKET_CAPACITY = int(os.getenv("TOKEN_BUCKET_CAPACITY", "5"))
TOKEN_BUCKET_REFILL_RATE = float(os.getenv("TOKEN_BUCKET_REFILL_RATE", "1"))

RATE_LIMIT_ALGORITHM = os.getenv("RATE_LIMIT_ALGORITHM", "token_bucket")