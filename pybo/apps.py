from django.apps import AppConfig
from .url_patterns import URLS

class PyboConfig(AppConfig):
    name = URLS['APP_NAME']

    def ready(self) -> None:
        """
        Django 앱이 로드될 때 호출되는 ready() 메서드에서 백그라운드 작업 파일을 명시적으로 임포트합니다.
        Django Background Task(DBT)는 비동기 태스크를 큐에 등록하는데, 이때 Django가 백그라운드 작업을 
        찾지 못하는 경우가 발생할 수 있습니다.
        특히 DBT는 @background 데코레이터를 사용하여 백그라운드 작업을 정의하지만, 해당 파일이 
        명시적으로 임포트되지 않으면 Django가 그 작업을 인식하지 못하여 실행되지 않습니다.

        여기에서 tasks.py 파일을 명시적으로 임포트함으로써 Django가 앱 로드 시 해당 작업을 
        인식하고, 백그라운드에서 비동기로 처리할 수 있도록 합니다.
        즉, 백그라운드 작업을 등록하고 스케줄링하기 위해 작업 파일을 강제로 불러오는 것입니다.
        이를 통해 Django가 백그라운드 작업을 적절히 처리하게 됩니다.
        """
        
        import pybo.tasks.task  # 백그라운드 작업을 정의한 파일을 명시적으로 임포트
