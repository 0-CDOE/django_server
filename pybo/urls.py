from django.urls import path

from .views import question_views, answer_views
from .url_patterns import URLS

app_name = URLS['APP_NAME']

def generate_board_urls(board_name, content_type, actions, views):
    """
    게시판과 콘텐츠 타입에 따른 URL 패턴을 생성하는 함수.
    
    :param board_name: 게시판 이름 (예: 'similarity', 'detection')
    :param content_type: 콘텐츠 타입 (예: 'post', 'comment')
    :param actions: CRUD 및 추가 동작 딕셔너리
    :param views: 뷰 모듈 딕셔너리
    :return: 생성된 URL 패턴 리스트
    """
    patterns = []

    # URL 패턴 형식을 사전으로 관리
    url_patterns = {
        'list': f'{board_name}/{content_type}/list/',
        'create': f'{board_name}/{content_type}/create/',  # create도 pk 없음
        'default': f'{board_name}/{content_type}/{{action}}/<int:pk>/'
    }
    
    for _, action in actions.items():
        try:
            # 'create'와 'list'의 경우는 기본 URL에 pk가 없음
            if action in ['create', 'list']:
                if content_type == 'post':
                    url_template = url_patterns[action]
                if content_type == 'comment':
                    if action == 'create':
                        # 여기에는 pk가 포함됨
                        url_template = f'{board_name}/{content_type}/{action}/<int:pk>/'
                    elif action == 'list':
                        url_template = url_patterns[action]
            # 나머지 action은 pk가 필요함 이 때 해당 action에 대한 key가 없다면 default로 처리
            else:
                url_template = url_patterns.get(action, url_patterns['default'])

            # URL 패턴에 액션을 삽입
            url_path = url_template.format(action=action)
            url_name = f'{board_name}_{content_type}_{action}'
            view = views[f'{content_type}_{action}']
            patterns.append(path(url_path, view.as_view(), name=url_name))

        except KeyError:
            # 해당하는 뷰가 없으면 건너뛰기
            continue

    return patterns


# 질문 및 답변 뷰들을 딕셔너리로 묶기
views = {
    'post_list': question_views.QuestionListView,
    'post_read': question_views.QuestionDetailView,
    'post_create': question_views.QuestionCreateView,
    'post_update': question_views.QuestionUpdateView,
    'post_delete': question_views.QuestionDeleteView,
    'post_vote': question_views.QuestionVoteView,
    
    'comment_create': answer_views.AnswerCreateView,
    'comment_update': answer_views.AnswerUpdateView,
    'comment_delete': answer_views.AnswerDeleteView,
    'comment_vote': answer_views.AnswerVoteView,
}

# URL 패턴 생성
urlpatterns = []

for board_name in URLS['BOARD_NAME'].values():
    for content_type in URLS['CONTENT_TYPE'].values():
        urlpatterns += generate_board_urls(board_name, content_type, URLS['CRUD_AND_MORE'], views)

# ==============================================================================
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
# .
# ----------------------------------------------------------------------