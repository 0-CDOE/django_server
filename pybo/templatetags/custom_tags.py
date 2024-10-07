from django import template
from django.urls import reverse

from ..url_patterns import URLS

register = template.Library()
@register.simple_tag(takes_context=True)
def url_byME(context, content_type, end_point, post_id=None, comment_id=None):
    """
    템플릿에서 content_type과 end_point만 넘기고,
    app_name과 board_name은 뷰에서 context로 전달받아 처리.
    """
    # 뷰에서 전달된 app_name과 board_name을 가져옴
    app_name = context.get('app_name')
    board_name = context.get('board_name')
    
    # app_name이 없으면 예외 발생
    if not app_name:
        raise ValueError("app_name is missing from context")
    if not board_name:
        raise ValueError("board_name is missing from context")
        
    # 기본 URL 형식 정의
    url = f'{app_name}:{board_name}_{content_type}_{end_point}'

    # post 타입 처리
    if content_type == 'post':
        if post_id:
            return reverse(url, kwargs={'pk': post_id})
        return reverse(url)  # obj_id가 필요 없는 경우 (ex. list)

    # comment 타입 처리
    elif content_type == 'comment':
        if comment_id:  # 댓글의 경우 comment_id 우선 처리
            return reverse(url, kwargs={'pk': comment_id})
        elif post_id:  # 만약 comment_id가 없고 obj_id만 있을 경우 fallback
            return reverse(url, kwargs={'pk': post_id})
        else:
            # 두 ID가 모두 없으면 기본 처리 또는 예외
            return reverse(url)  # 기본 URL로 반환 (list URL 같은 경우)

    # 잘못된 content_type 처리
    raise ValueError("Invalid content_type")


@register.simple_tag(takes_context=True)
def board_name_for_user(context):
    board_name_for_user = {
        'similarity': '얼굴 유사도 비교',
        'detection': '대통령을 찾아라!',
    }
    return board_name_for_user[context.get('board_name')]

@register.simple_tag(takes_context=True)
def board_explanation(context):
    board_explanation = {
        'similarity': '얼굴 사진을 업로드하면 유사도를 비교해드립니다.',
        'detection': '대통령 사진을 업로드하면 대통령을 찾아드립니다.',
    }
    return board_explanation[context.get('board_name')]

@register.simple_tag(takes_context=True)
def board_list(context):
    
    return reverse(f'{context.get("app_name")}:{context.get("board_name")}_post_list')

