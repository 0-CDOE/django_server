from django.test import TestCase
from pybo.urls import urlpatterns

class URLPatternTest(TestCase):
    """
    URL 패턴을 테스트하는 클래스입니다.
    
    Django 프로젝트의 URL 패턴을 순회하면서 각 패턴의 경로와 이름을 출력하는 테스트입니다.
    
    Methods
    -------
    test_url_patterns():
        urlpatterns 리스트에 정의된 각 URL 패턴을 순회하면서 경로와 이름을 출력합니다.
    """
    
    def test_url_patterns(self):
        """
        urlpatterns 리스트에 정의된 URL 패턴을 순회하면서 각 패턴의 경로와 이름을 출력합니다.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        # 테스트 시작을 알리는 출력
        print('URL Pattern Test Start!')
        
        # urlpatterns 리스트에 있는 URL 패턴을 하나씩 순회
        for pattern in urlpatterns:
            try:
                # URL 패턴의 경로와 이름을 출력
                print(f'URL Pattern: {pattern.pattern} | Name: {pattern.name}')
            except AttributeError:
                # 만약 패턴에 .pattern이나 .name 속성이 없는 경우 예외 처리
                print(f'Invalid pattern: {pattern}')
        
        # 테스트 종료를 알리는 출력
        print('URL Pattern Test Done!')
