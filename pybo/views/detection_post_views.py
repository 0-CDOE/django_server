from .base_views import BaseListView, BaseReadView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionPost
from ..forms import DetectionPostForm, DetectionCommentForm
from .detection_comment_views import create_initial_ai_answer2

from ..url_patterns import URLS

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['detection']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 url 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'


import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성


class ExtraContextMixin(BaseExtraContextMixin):
    """
    ExtraContextMixin 클래스는 모든 뷰에서 공통적으로 사용할 추가 데이터를 템플릿 컨텍스트에 전달합니다.
    """

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        게시판 이름 및 댓글 폼을 컨텍스트에 추가하여 템플릿에서 사용할 수 있도록 합니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = DetectionCommentForm()  # 댓글 폼 추가
        return context


class DetectionPostListView(ExtraContextMixin, BaseListView):
    """
    DetectionPostListView 클래스는 특정 인물 찾기 게시판의 게시글 목록을 표시하는 뷰입니다.

    검색 필드를 설정하여 게시글 제목, 내용, 작성자 이름으로 검색할 수 있습니다.
    """

    model = DetectionPost  # 모델 설정
    template_name = 'pybo/question_list.html'  # 템플릿 설정
    search_fields = ['subject', 'content', 'author__username']  # 검색 필드 설정


class DetectionPostReadView(ExtraContextMixin, BaseReadView):
    """
    DetectionPostReadView 클래스는 특정 인물 찾기 게시판의 게시글 상세 내용을 표시하는 뷰입니다.
    """

    model = DetectionPost  # 모델 설정
    template_name = 'pybo/question_detail.html'  # 템플릿 설정


class DetectionPostCreateView(ExtraContextMixin, BaseCreateView):
    """
    DetectionPostCreateView 클래스는 특정 인물 찾기 게시판의 게시글을 작성하는 뷰입니다.

    AI 탐지기 및 예측기를 선택하여 추가 작업을 수행할 수 있습니다.
    """

    model = DetectionPost  # 모델 설정
    form_class = DetectionPostForm  # 폼 클래스 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 설정

    def form_valid(self, form):
        """
        폼이 유효한 경우 AI 처리 로직을 실행하고 게시글을 저장하는 메서드입니다.
        """
        response = super().form_valid(form)

        post = form.instance  # 저장된 게시글 인스턴스 가져오기
        
        logger.info(f"AI 처리 시작 - 질문: {post}")
        try:
            create_initial_ai_answer2(post_id=post.id)
            logger.info(f"AI 처리 완료 - 질문 ID: {post}")
        except Exception as e:
            logger.error(f"AI 처리 실패 - 질문 ID: {post}, 에러: {str(e)}")

        return response


class DetectionPostUpdateView(ExtraContextMixin, BaseUpdateView):
    """
    DetectionPostUpdateView 클래스는 특정 인물 찾기 게시판의 게시글을 수정하는 뷰입니다.
    """

    model = DetectionPost  # 모델 설정
    form_class = DetectionPostForm  # 폼 클래스 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 설정


class DetectionPostDeleteView(ExtraContextMixin, BaseDeleteView):
    """
    DetectionPostDeleteView 클래스는 특정 인물 찾기 게시판의 게시글을 삭제하는 뷰입니다.
    """

    model = DetectionPost  # 모델 설정
    success_url = list_url  # 성공 후 리다이렉트할 URL


class DetectionPostVoteView(ExtraContextMixin, BaseVoteView):
    """
    DetectionPostVoteView 클래스는 특정 인물 찾기 게시판의 게시글에 대해 추천하는 기능을 담당하는 뷰입니다.
    """

    model = DetectionPost  # 모델 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
