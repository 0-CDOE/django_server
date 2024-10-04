from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def url_byME(context, content_type, end_point, obj_id=None, comment_id=None):
    """
    템플릿에서 content_type과 end_point만 넘기고,
    app_name과 board_name은 뷰에서 context로 전달받아 처리.
    """
    # 뷰에서 전달된 app_name과 board_name을 가져옴
    app_name = context.get('app_name')
    board_name = context.get('board_name')

    # app_name과 board_name이 없으면 예외 발생
    if not app_name or not board_name:
        raise ValueError("app_name or board_name is missing from context")

    # 기본 URL 형식 정의
    url = f'{app_name}:{board_name}_{content_type}_{end_point}'

    # post 타입 처리
    if content_type == 'post':
        if obj_id:
            return reverse(url, kwargs={'pk': obj_id})
        return reverse(url)  # obj_id가 필요 없는 경우 (ex. list)

    # comment 타입 처리
    elif content_type == 'comment':
        if obj_id:
            return reverse(url, kwargs={'pk': obj_id})
        elif comment_id:
            return reverse(url, kwargs={'pk': comment_id})
        else:
            raise ValueError("Both obj_id and comment_id are missing for 'comment' content_type")

    # 잘못된 content_type 처리
    raise ValueError("Invalid content_type")
