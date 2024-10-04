# from types import SimpleNamespace

# URLS = SimpleNamespace(
#     APP_NAME='pybo',
#     DETAIL_URL='detail',
#     INDEX_URL='index',
#     QUESTION_CREATE_URL='question_create',
#     QUESTION_UPDATE_URL='question_update',
#     QUESTION_DELETE_URL='question_delete',
#     QUESTION_VOTE_URL='question_vote'
# )

# 위 처럼 URLS를 정의하고 사용하면 F2로 이름을 변경할 수 없음.

URLS = {
    'APP_NAME': 'pybo',
    'BOARD_NAME': {
        'similarity': 'similarity',
        'detection': 'detection'
    },
    'CONTENT_TYPE': {
        'post': 'post',
        'comment': 'comment'
    },
    'CRUD_AND_MORE': {
        'create': 'create',
        'read': 'read',
        'update': 'update',
        'delete': 'delete',
        'vote': 'vote',
        'list': 'list'
    },
}
