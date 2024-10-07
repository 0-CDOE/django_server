from .base_views import BaseListView, BaseReadView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import SimilarityPost
from ..forms import SimilarityPostForm, SimilarityCommentForm
from .similarity_comment_views import create_initial_ai_comment

from ..url_patterns import URLS

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['similarity']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'

import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성

"""
이 모듈은 BaseListView, BaseReadView, BaseCreateView, BaseUpdateView 등의 공통 뷰 클래스를 상속받아,
유사도 게시판에 관련된 뷰를 정의합니다.
템플릿에서 사용할 모델 객체는 'object'로 사용됩니다.

1. 템플릿에서 해당 모델에 정의된 모든 필드와 메서드에 접근할 수 있습니다. (ex. object.author.username)
2. 템플릿에서 모델이 다른 모델과 연결된 경우, 관련된 모델 객체에도 접근할 수 있습니다. (ex. object.comments.all())
3. 템플릿에서 Django 모델의 메타 정보를 사용할 수도 있습니다. (ex. object._meta.verbose_name)
"""

class SimilarityPostExtraContextMixin(BaseExtraContextMixin):
    """
    게시판에 공통적으로 사용할 추가 데이터를 템플릿에 전달하는 믹스인 클래스입니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 전달할 추가적인 데이터를 설정합니다.
    """

    def get_context_data(self, **kwargs) -> dict:
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        게시판 이름과 댓글 폼을 템플릿에 전달하여 사용할 수 있도록 합니다.

        Parameters
        ----------
        **kwargs : dict
            템플릿에 전달할 추가적인 인자들입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 메서드 호출
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = SimilarityCommentForm()  # 댓글 폼 추가
        return context


class SimilarityPostListView(SimilarityPostExtraContextMixin, BaseListView):
    """
    유사도 게시판의 게시글 목록을 보여주는 뷰입니다.
    검색 기능을 제공하여 제목, 내용, 작성자 이름으로 검색할 수 있습니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
        
    search_fields : list
        검색 가능한 필드를 설정합니다.
    """

    model = SimilarityPost  # 모델 설정
    template_name = 'pybo/question_list.html'  # 템플릿 파일 경로
    search_fields = ['subject', 'content', 'author__username']  # 검색할 필드 설정


class SimilarityPostCreateView(SimilarityPostExtraContextMixin, BaseCreateView):
    """
    유사도 게시판의 게시글을 작성하는 뷰입니다.
    게시글 작성 후 AI 처리를 추가로 수행할 수 있습니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    form_class : Form
        사용할 폼 클래스를 설정합니다.
        
    success_url : str
        게시글 작성 후 리다이렉트할 URL입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """

    model = SimilarityPost  # 모델 설정
    form_class = SimilarityPostForm  # 사용할 폼 클래스 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 파일 경로

    def form_valid(self, form) -> 'HttpResponseRedirect':
        """
        폼이 유효한 경우 AI 처리 로직을 실행하고 게시글을 저장합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            작성된 게시글의 상세 페이지로 리다이렉트됩니다.
        """
        # 부모 클래스의 form_valid 메서드 호출
        response = super().form_valid(form)

        # 추가 작업 (AI 처리 로직)
        post = form.instance  # 저장된 게시글 인스턴스 가져오기
        logger.info(f"AI 처리 시작 - 질문: {post}")

        try:
            create_initial_ai_comment(post_id=post.id)
            logger.info(f"AI 처리 완료 - 질문 ID: {post}")
        except Exception as e:
            logger.error(f"AI 처리 실패 - 질문 ID: {post}, 에러: {str(e)}")

        return response  # 부모 클래스의 form_valid 메서드 결과 반환


class SimilarityPostReadView(SimilarityPostExtraContextMixin, BaseReadView):
    """
    유사도 게시판의 게시글 상세 내용을 보여주는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """

    model = SimilarityPost  # 모델 설정
    template_name = 'pybo/question_detail.html'  # 템플릿 파일 경로


class SimilarityPostUpdateView(SimilarityPostExtraContextMixin, BaseUpdateView):
    """
    유사도 게시판의 게시글을 수정하는 뷰입니다.
    게시글 수정 후 AI 처리는 구현되지 않았습니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    form_class : Form
        사용할 폼 클래스를 설정합니다.
        
    success_url : str
        게시글 수정 후 리다이렉트할 URL입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """

    model = SimilarityPost  # 모델 설정
    form_class = SimilarityPostForm  # 폼 클래스 설정
    success_url = read_url  # 수정 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 파일 경로


class SimilarityPostDeleteView(SimilarityPostExtraContextMixin, BaseDeleteView):
    """
    유사도 게시판의 게시글을 삭제하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    success_url : str
        게시글 삭제 후 리다이렉트할 URL입니다.
    """

    model = SimilarityPost  # 모델 설정
    success_url = list_url  # 삭제 후 리다이렉트할 URL


class SimilarityPostVoteView(SimilarityPostExtraContextMixin, BaseVoteView):
    """
    유사도 게시판의 게시글에 추천 기능을 제공하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 Django 모델입니다.
        
    success_url : str
        게시글 추천 후 리다이렉트할 URL입니다.
    """

    model = SimilarityPost  # 모델 설정
    success_url = read_url  # 추천 후 리다이렉트할 URL
