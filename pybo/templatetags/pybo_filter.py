import markdown
from django import template
from django.utils.safestring import mark_safe

# 템플릿 라이브러리 객체 생성
register = template.Library()

# 필터 함수 정의 및 등록
@register.filter
def sub(value, arg):
    return value - arg
"""

mark 함수는 markdown 모듈과 mark_safe 함수를 이용하여 입력 문자열을 HTML로 변환하는 필터 함수이다. 

마크다운에는 몇 가지 확장 기능이 있는데 파이보는 위처럼 nl2br과 fenced_code를 사용하도록 설정했다. 

nl2br은 줄바꿈 문자를 <br> 로 바꾸어 준다. fenced_code는 위에서 살펴본 마크다운의 소스코드 표현을 위해 필요하다.

nl2br을 사용하지 않을 경우 줄바꿈을 하기 위해서는 줄 끝에 스페이스(' ')를 두개 연속으로 입력해야 한다.

마크다운의 더 많은 확장 기능은 다음 문서를 참고하자.

마크다운 확장 기능 문서: https://python-markdown.github.io/extensions/

"""
@register.filter
def mark(value):
    if value is None :
        value = ""
    extensions = ["nl2br", "fenced_code"]
    return mark_safe(markdown.markdown(value, extensions=extensions))