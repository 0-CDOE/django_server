import os
import environ

from .base import *

ALLOWED_HOSTS = ['3.34.71.98']
STATIC_ROOT = BASE_DIR / 'static/'

"""
base.py 파일에 STATICFILES_DIRS 항목이 이미 있는데 prod.py 파일에 다시 빈 값으로 설정하는 이유는 

STATIC_ROOT가 설정된 경우 STATICFILES_DIRS 리스트에 STATIC_ROOT와 동일한 디렉터리가 포함되어 있으면 

서버 실행 시 오류가 발생하기 때문이다.
"""
STATICFILES_DIRS = []

# 프로젝트 루트 디렉토리를 기준으로 경로 설정
env = environ.Env(
    DEBUG=(bool, False) # DEBUG 변수의 기본값은 False
)

# .env 파일을 로드합니다.
environ.Env.read_env(os.path.join(BASE_DIR, '.env')) 

# 디버그 모드 비활성화
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

# MySQL 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pyboDB',
        'USER': 'AdminParkDB',
        'PASSWORD': 'alrk08642',
        'HOST': 'ls-2a4d43344121d1c3ef988f7729390afcdaaf899d.ch42m0omuy1q.ap-northeast-2.rds.amazonaws.com',
        'PORT': '3306',
    }
}