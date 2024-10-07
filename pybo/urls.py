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
def get_view_class(board_name, content_type, action):
    """
    주어진 게시판, 콘텐츠 타입, 액션에 맞는 뷰 클래스를 반환합니다.
    
    :param board_name: 게시판 이름 ('similarity' 또는 'detection')
    :param content_type: 'post' 또는 'comment'
    :param action: CRUD 액션 ('list', 'read', 'create', 'update', 'delete', 'vote')
    :return: 해당하는 뷰 클래스
    """
    module = VIEW_MODULES[board_name][content_type]
    action_map = {
        'list': 'ListView' if content_type == 'post' else None,  # comment에는 list가 없음
        'read': 'ReadView' if content_type == 'post' else None,  # comment에는 read가 없음
        'create': 'CreateView',
        'update': 'UpdateView',
        'delete': 'DeleteView',
        'vote': 'VoteView'
    }
    
    view_class_name = action_map.get(action)
    
    # view_class_name이 None인 경우 처리하지 않음
    if view_class_name is None:
        return None
    
    view_class_name = f"{board_name.capitalize()}{content_type.capitalize()}{view_class_name}"
    return getattr(module, view_class_name, None)

# URL 템플릿을 가져오는 함수
def get_url_template(board_name, content_type, action):
    """
    URL 템플릿을 가져오는 함수
    
    :param board_name: 게시판 이름
    :param content_type: 콘텐츠 타입
    :param action: CRUD 액션
    :return: URL 템플릿
    """
    url_templates = {
        'list': f'{board_name}/{content_type}/list/',
        'create': f'{board_name}/{content_type}/create/' if content_type == 'post' else f'{board_name}/{content_type}/create/<int:pk>/',  # post는 pk가 없지만 comment는 pk가 있음
        'default': f'{board_name}/{content_type}/{action}/<int:pk>/'
    }
    
    return url_templates.get(action, url_templates['default'].format(action=action))

# URL 패턴 생성 함수
def generate_board_urls(board_name, content_type, actions):
    """
    게시판과 콘텐츠 타입에 따른 URL 패턴을 생성하는 함수.
    
    :param board_name: 게시판 이름
    :param content_type: 'post' 또는 'comment'
    :param actions: CRUD 액션 딕셔너리
    :return: URL 패턴 리스트
    """
    patterns = []
    for action in actions.values():
        # 뷰 클래스 동적으로 가져오기
        view_class = get_view_class(board_name, content_type, action)
        
        # view_class가 None인 경우 건너뜀
        if view_class is None:
            continue
        
        # URL 템플릿 가져오기
        url_template = get_url_template(board_name, content_type, action)
        url_name = f'{board_name}_{content_type}_{action}'
        
        # URL 패턴 추가
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
# =======================================================================================
# URL Pattern Test Start!
# URL Pattern: similarity/post/create/ | Name : similarity_post_create
# URL Pattern: similarity/post/read/<int:pk>/ | Name : similarity_post_read
# URL Pattern: similarity/post/update/<int:pk>/ | Name : similarity_post_update
# URL Pattern: similarity/post/delete/<int:pk>/ | Name : similarity_post_delete
# URL Pattern: similarity/post/vote/<int:pk>/ | Name : similarity_post_vote
# URL Pattern: similarity/post/list/ | Name : similarity_post_list
# URL Pattern: similarity/comment/create/<int:pk>/ | Name : similarity_comment_create
# URL Pattern: similarity/comment/update/<int:pk>/ | Name : similarity_comment_update
# URL Pattern: similarity/comment/delete/<int:pk>/ | Name : similarity_comment_delete
# URL Pattern: similarity/comment/vote/<int:pk>/ | Name : similarity_comment_vote
# URL Pattern: detection/post/create/ | Name : detection_post_create
# URL Pattern: detection/post/read/<int:pk>/ | Name : detection_post_read
# URL Pattern: detection/post/update/<int:pk>/ | Name : detection_post_update
# URL Pattern: detection/post/delete/<int:pk>/ | Name : detection_post_delete
# URL Pattern: detection/post/vote/<int:pk>/ | Name : detection_post_vote
# URL Pattern: detection/post/list/ | Name : detection_post_list
# URL Pattern: detection/comment/create/<int:pk>/ | Name : detection_comment_create
# URL Pattern: detection/comment/update/<int:pk>/ | Name : detection_comment_update
# URL Pattern: detection/comment/delete/<int:pk>/ | Name : detection_comment_delete
# URL Pattern: detection/comment/vote/<int:pk>/ | Name : detection_comment_vote
# URL Pattern Test Done!