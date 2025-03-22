import os
import random
from dotenv import load_dotenv, dotenv_values

from .base import *

# 먼저 루트의 .env 파일을 로드해서 MODE 등 기본 환경변수를 설정합니다.
load_dotenv(os.path.join(BASE_DIR, ".env"))

# .env 파일에 정의된 MODE 값을 읽어오며, 없으면 기본값은 "prod"로 사용합니다.
mode = os.getenv("MODE", "local")

# MODE에 따라 해당하는 env 파일을 로드합니다. 예를 들어, MODE가 prod라면 prod.env 파일을 로드합니다.
ENV = dotenv_values(os.path.join(BASE_DIR, f"{mode}.env"))


# 🛠 PATH 환경 변수에 추가
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

SECRET_KEY = ENV.get(
    "DJANGO_SECRET_KEY",
    "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()?", k=50)),
)

ROOT_URLCONF = "config.urls"

DEBUG = True

# Database 설정
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("POSTGRES_HOST", "db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "NAME": os.getenv("POSTGRES_DBNAME", "claim"),
        "PORT": os.getenv("POSTGRES_PORT", 5432),
    }
}

# Static
STATIC_URL = "/static/"
STATIC_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / ".static_root"

# Media
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# OAuth
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

backend_url = os.getenv("BACKEND_BASE_URL", "").rstrip("/")
KAKAO_CALLBACK_URL = f"{backend_url}/v1/users/login/kakao/callback/"
BACKEND_BASE_URL = f"{backend_url}"

frontend_url = os.getenv("FRONTEND_BASE_URL", "").rstrip("/")
FRONTEND_CALLBACK_URL = f"{frontend_url}/login/?code="


crawler_apr_url = os.getenv("CRAWLER_API_URL", "http://localhost:5000")
All_CRAWLER_API_URL = f"{crawler_apr_url}/insurance_all_crawler" # 내보험 다보여
SIMPLE_CRAWLER_API_URL = f"{crawler_apr_url}/insurance_simple_crawler" # 내보험 보여줌

crawler_callback_base_url= os.getenv("CRAWLER_CALLBACK_BASE_URL","http://localhost:8000")
CRAWLER_CALLBACK_URL = f"{crawler_callback_base_url}/v1/insurances/call_back_crawler/"
