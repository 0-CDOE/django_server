from django import template  # Django 템플릿 라이브러리
from django.utils.safestring import mark_safe  # 안전한 HTML 문자열로 변환하는 함수
import markdown  # 마크다운 문자열을 HTML로 변환하기 위한 모듈

# 템플릿 필터를 등록하기 위한 Library 객체 생성
register = template.Library()

@register.filter
def sub(value, arg):
    """
    'subtract' 필터는 템플릿에서 value에서 arg를 뺀 결과를 반환합니다.

    템플릿에서 사용 시:
    {{ value|subtract:arg }} 형태로 사용되어 value - arg 결과를 출력합니다.

    Args:
        value (int, float): 뺄셈의 피연산자
        arg (int, float): 뺄셈할 값

    Returns:
        int, float: value에서 arg를 뺀 결과값
    """
    try:
        return value - arg
    except TypeError:
        return 0  # 값이 없을 경우 0을 반환

@register.filter
def md_to_html(value):
    """
    'render_markdown' 필터는 마크다운 문자열을 HTML로 변환하고,
    안전한 HTML로 처리하여 반환합니다.

    마크다운 확장 기능:
    - 'nl2br': 줄바꿈을 <br> 태그로 변환합니다.
    - 'fenced_code': 코드 블록을 처리합니다.

    사용 예:
    {{ value|render_markdown }} 형태로 템플릿에서 사용하여
    마크다운을 HTML로 변환할 수 있습니다.

    Args:
        value (str): 변환할 마크다운 문자열

    Returns:
        str: HTML로 변환된 안전한 문자열
    """

    if value is None:
        value = ""

    # 마크다운 확장 기능 설정
    extensions =  [
        "markdown.extensions.extra", 
        "markdown.extensions.nl2br", 
        "markdown.extensions.fenced_code"
        ]

    # 마크다운을 HTML로 변환하고, 안전한 HTML로 처리하여 반환
    return mark_safe(markdown.markdown(value, extensions=extensions))

@register.filter
def add_class(field, css_class):
    """
    'add_css_class' 필터는 폼 필드에 CSS 클래스를 추가합니다.

    템플릿에서 사용 시:
    {{ field|add_css_class:'class-name' }} 형태로 사용되어
    해당 필드에 지정된 CSS 클래스를 추가합니다.

    Args:
        field (Field): Django 폼 필드 객체
        css_class (str): 추가할 CSS 클래스 이름

    Returns:
        Widget: 주어진 필드에 CSS 클래스를 적용한 위젯
    """
    return field.as_widget(attrs={"class": css_class})

@register.filter
def zip_lists(a, b):
    """두 리스트를 zip으로 묶어준다"""
    return zip(a, b)

