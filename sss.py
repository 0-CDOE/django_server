from django.urls import path
from .views import similarity_comment_views, similarity_post_views, detection_post_views, detection_comment_views, base_views
from .url_patterns import URLS

app_name = URLS['APP_NAME']

# 게시판별로 사용할 모듈을 사전에 정의하여 반복을 줄임
VIEW_MODULES = {
    'similarity': {
        'post': similarity_post_views,
        'comment': similarity_comment_views
    },
    'detection': {
        'post': detection_post_views,
        'comment': detection_comment_views
    }
}

# CRUD 액션에 맞는 View 이름을 자동으로 찾는 함수
def get_view_class(board_name: str, content_type: str, action: str):

    # 게시판과 콘텐츠 타입에 맞는 모듈을 가져옴
    module = VIEW_MODULES[board_name][content_type]
    
    # CRUD 액션에 맞는 뷰 이름을 매핑
    action_map = {
        'list': 'ListView' if content_type == 'post' else None,  # comment에는 list가 없음
        'read': 'ReadView' if content_type == 'post' else None,  # comment에는 read가 없음
        'create': 'CreateView',
        'update': 'UpdateView',
        'delete': 'DeleteView',
        'vote': 'VoteView'
    }
    
    # 액션에 맞는 View 클래스 이름을 가져옴
    view_class_name = action_map.get(action)
    
    # View 클래스가 존재하지 않으면 None 반환
    if view_class_name is None:
        return None
    
    # 동적으로 View 클래스를 가져옴
    view_class_name = f"{board_name.capitalize()}{content_type.capitalize()}{view_class_name}"
    return getattr(module, view_class_name, None)

# URL 템플릿을 가져오는 함수
def get_url_template(board_name: str, content_type: str, action: str) -> str:

    # 액션에 맞는 URL 템플릿 매핑
    url_templates = {
        'list': f'{board_name}/{content_type}/list/',
        'create': f'{board_name}/{content_type}/create/' if content_type == 'post' else f'{board_name}/{content_type}/create/<int:pk>/',  # post는 pk가 없고 comment는 pk가 있음
        'default': f'{board_name}/{content_type}/{action}/<int:pk>/'
    }
    
    # 액션에 맞는 템플릿 반환
    return url_templates.get(action, url_templates['default'].format(action=action))

# URL 패턴 생성 함수
def generate_board_urls(board_name: str, content_type: str, actions: dict) -> list:

    # URL 패턴을 저장할 리스트
    patterns = []
    
    # 각 액션에 대해 URL 패턴 생성
    for action in actions.values():
        # 동적으로 View 클래스 가져오기
        view_class = get_view_class(board_name, content_type, action)
        
        # View 클래스가 None인 경우 건너뜀
        if view_class is None:
            continue
        
        # URL 템플릿과 URL 이름 설정
        url_template = get_url_template(board_name, content_type, action)
        url_name = f'{board_name}_{content_type}_{action}'
        
        # URL 패턴을 추가
        patterns.append(path(url_template, view_class.as_view(), name=url_name))
    
    return patterns

# =======================================================================================

# URL 패턴 생성
urlpatterns = []

# 게시판별로 URL 패턴 생성
for board_name in URLS['BOARD_NAME'].values():
    for content_type in URLS['CONTENT_TYPE'].values():
        urlpatterns += generate_board_urls(board_name, content_type, URLS['CRUD_AND_MORE'])

# 공통 URL 패턴 추가
urlpatterns += [
    path('', base_views.IndexView.as_view(), name='index'),
]
