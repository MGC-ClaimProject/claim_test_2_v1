# ✅ Python 3.13 기반 이미지 사용
FROM python:3.13

# ✅ 작업 디렉토리 설정
WORKDIR /app/src

# ✅ 패키지 설치 및 업데이트 (Selenium 관련 패키지 제거됨)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ✅ Poetry 설치
RUN pip install --no-cache-dir poetry

# ✅ Poetry 환경 설정
RUN poetry config virtualenvs.create false

# ✅ 프로젝트 의존성 설치
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# ✅ 형제 폴더인 scripts 복사 (경로 수정)
COPY src/scripts /app/src/scripts

# ✅ 실행 권한 부여
RUN chmod +x /app/src/scripts/entrypoint.sh

# ✅ 프론트엔드 빌드 파일 복사
COPY frontend/dist /usr/share/nginx/html

# ✅ 백엔드 코드 복사
COPY src .

# ✅ Django 환경 변수 설정
ENV PYTHONPATH="/app"

# ✅ 엔트리포인트 설정
ENTRYPOINT ["sh", "/app/src/scripts/entrypoint.sh"]
