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

# 리다이렉트 url 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'


import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성

"""
이 모듈은 BaseListView, BaseReadView, BaseCreateView, BaseUpdateView 등 공통 뷰 클래스를 상속받아,
게시판 뷰를 정의합니다. 템플릿에서 사용할 모델 객체 이름은 'object'로 사용합니다.

1. 템플릿에서 해당 모델에 정의된 모든 필드와 메서드에 접근할 수 있습니다. (ex. object.author.username)

2. 템플릿에서 모델이 다른 모델과 연결된 경우, 관련된 모델 객체에도 접근할 수 있습니다. 
   (ex. object.comments.all())

3. 템플릿에서 Django 모델의 메타 정보를 사용할 수도 있습니다. (ex. object._meta.verbose_name)
"""


class ExtraContextMixin(BaseExtraContextMixin):
    """
    ExtraContextMixin 클래스는 모든 뷰에서 공통적으로 사용할 추가 데이터를 템플릿 컨텍스트에 전달합니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 추가적인 데이터를 설정합니다.
    """
    
    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        게시판 이름 및 댓글 폼을 컨텍스트에 추가하여 템플릿에서 사용할 수 있도록 합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = SimilarityCommentForm()  # 댓글 폼 추가
        return context


class SimilarityPostListView(ExtraContextMixin, BaseListView):
    """
    SimilarityPostListView 클래스는 유사도 게시판의 게시글 목록을 표시하는 뷰입니다.

    검색 필드를 설정하여 게시글 제목, 내용, 작성자 이름으로 검색할 수 있습니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    template_name : str
        사용할 템플릿 파일의 경로입니다.
        
    search_fields : list
        검색 가능한 필드를 지정합니다.
    """
    
    model = SimilarityPost  # 모델 설정
    template_name = 'pybo/question_list.html'  # 템플릿 설정
    search_fields = ['subject', 'content', 'author__username']  # 검색 필드 설정


class SimilarityPostReadView(ExtraContextMixin, BaseReadView):
    """
    SimilarityPostReadView 클래스는 유사도 게시판의 게시글 상세 내용을 표시하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    template_name : str
        사용할 템플릿 파일의 경로입니다.
    """
    
    model = SimilarityPost  # 모델 설정
    template_name = 'pybo/question_detail.html'  # 템플릿 설정


class SimilarityPostCreateView(ExtraContextMixin, BaseCreateView):
    """
    SimilarityPostCreateView 클래스는 유사도 게시판의 게시글을 작성하는 뷰입니다.

    AI 탐지기 및 예측기를 선택하여 추가 작업을 수행할 수 있습니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    form_class : Form
        사용할 폼 클래스를 설정합니다.
        
    success_url : str
        게시글 작성 후 리다이렉트할 URL을 설정합니다.
        
    template_name : str
        사용할 템플릿 파일의 경로입니다.
        
    Methods
    -------
    form_valid(form):
        폼이 유효한 경우 AI 처리 로직을 실행하고, 게시글을 저장합니다.
    """

    model = SimilarityPost  # 모델 설정
    form_class = SimilarityPostForm  # 폼 클래스 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 설정

    def form_valid(self, form):
        """
        폼이 유효한 경우 AI 처리 로직을 실행하고 게시글을 저장하는 메서드입니다.

        선택된 AI 탐지기 및 예측기를 바탕으로 AI 작업을 수행합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            작성된 게시글의 상세 페이지로 리다이렉트합니다.
        """
        # 상위 클래스의 form_valid 호출 (기존 동작 유지)
        response = super().form_valid(form)

        # 추가 작업 (AI 처리 로직)을 여기에 정의
        post = form.instance  # 저장된 게시글 인스턴스 가져오기

        # 선택된 AI 탐지기 및 예측기 처리
        # selected_detectors = self.request.POST.getlist('detectors')  # 탐지기 목록 가져오기
        # selected_predictors = self.request.POST.getlist('predictors')  # 예측기 목록 가져오기

        logger.info(f"AI 처리 시작 - 질문: {post}")
        try:
            create_initial_ai_comment(post_id=post.id,)
            logger.info(f"AI 처리 완료 - 질문 ID: {post}")
        except Exception as e:
            logger.error(f"AI 처리 실패 - 질문 ID: {post}, 에러: {str(e)}")
        
        return response  # 상위 클래스의 결과 반환


class SimilarityPostUpdateView(ExtraContextMixin, BaseUpdateView):
    """
    SimilarityPostUpdateView 클래스는 유사도 게시판의 게시글을 수정하는 뷰입니다.

    AI 처리 로직은 구현되지 않으며, 게시글 수정만 처리됩니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    form_class : Form
        사용할 폼 클래스를 설정합니다.
        
    success_url : str
        게시글 수정 후 리다이렉트할 URL을 설정합니다.
    """
    
    model = SimilarityPost  # 모델 설정
    form_class = SimilarityPostForm  # 폼 클래스 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
    template_name = 'pybo/question_form.html'  # 템플릿 설정


class SimilarityPostDeleteView(ExtraContextMixin, BaseDeleteView):
    """
    SimilarityPostDeleteView 클래스는 유사도 게시판의 게시글을 삭제하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    success_url : str
        게시글 삭제 후 리다이렉트할 URL을 설정합니다.
    """
    
    model = SimilarityPost  # 모델 설정
    success_url = list_url  # 성공 후 리다이렉트할 URL


class SimilarityPostVoteView(ExtraContextMixin, BaseVoteView):
    """
    SimilarityPostVoteView 클래스는 유사도 게시판의 게시글에 대해 추천하는 기능을 담당하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 설정합니다.
        
    success_url_post : str
        게시글 추천 후 리다이렉트할 URL을 설정합니다.
    """
    
    model = SimilarityPost  # 모델 설정
    success_url = read_url  # 성공 후 리다이렉트할 URL
