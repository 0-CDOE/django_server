import os

import environ

import PIL
from .base import *

ALLOWED_HOSTS = []

# 프로젝트 루트 디렉토리를 기준으로 경로 설정
env = environ.Env(
    DEBUG=(bool, False) # DEBUG 변수의 기본값은 False
)

# .env 파일을 로드합니다.
environ.Env.read_env(os.path.join(BASE_DIR, '.env')) 

# 디버그 모드 비활성화
DEBUG = True
SECRET_KEY = env('SECRET_KEY')