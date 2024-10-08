"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

application = get_wsgi_application()

import subprocess

def run_process_tasks():
    try:
        # subprocess.run()을 사용하여 명령어 실행
        result = subprocess.run(
            ['python', 'manage.py', 'process_tasks'],
            check=True,            # 오류 발생 시 예외 발생
            capture_output=True,    # 출력 캡처
            text=True               # 출력을 문자열로 변환
        )
        # 실행 결과 출력
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

# 함수 실행
run_process_tasks()
