from django.test import TestCase
from pybo.urls import urlpatterns

class URLPatternTest(TestCase):
    def test_url_patterns(self):
        """
        URL 패턴을 출력하는 테스트
        """
        print('URL Pattern Test Start!')
        for pattern in urlpatterns:
            try:
                # 각 패턴의 URL 경로와 뷰 이름을 출력
                print(f'URL Pattern: {pattern.pattern} | Name : {pattern.name}')
            except AttributeError:
                # 패턴에 패턴이나 이름이 없는 경우 예외 처리
                print(f'Invalid pattern: {pattern}')
        print('URL Pattern Test Done!')
