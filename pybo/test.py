from django.test import TestCase
from pybo.urls import urlpatterns

class URLPatternTest(TestCase):
    """
    URL 패턴을 테스트하는 클래스입니다.
    
    Django 프로젝트의 URL 패턴을 순회하면서 각 패턴의 경로, 이름, 그리고 연결된 View 클래스를 출력하는 테스트입니다.
    """
    
    def test_url_patterns(self):
        """
        urlpatterns 리스트에 정의된 URL 패턴을 순회하면서 각 패턴의 경로, 이름, 연결된 View 클래스를 출력합니다.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        # 테스트 시작을 알리는 출력
        print("\n===== URL Pattern Test Start! =====\n")
        
        # 테이블 헤더 출력
        print(f"| {'URL Pattern':<40} | {'URL_Name':<20} | {'View':<25} |")
        print(f"|{'-'*42}|{'-'*22}|{'-'*32}|")
        
        # urlpatterns 리스트에 있는 URL 패턴을 하나씩 순회
        for pattern in urlpatterns:
            try:
                # URL 패턴의 경로와 이름을 출력
                view_name = pattern.callback.view_class.__name__ if hasattr(pattern.callback, 'view_class') else pattern.callback.__name__
                
                print(f"| {str(pattern.pattern):<40} | {str(pattern.name):<20} | {view_name:<25} |")
                
            except AttributeError:
                # 만약 패턴에 .pattern이나 .name 속성이 없는 경우 예외 처리
                print(f"| Invalid pattern: {pattern:<40} | {'N/A':<20} | {'N/A':<25} |")
        
        # 테스트 종료를 알리는 출력
        print("\n===== URL Pattern Test Done! =====\n")
