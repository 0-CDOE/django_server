from .base_views import BaseListView, BaseReadView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionPostModel
from ..forms import DetectionPostForm, DetectionCommentForm
from .detection_comment_views import create_initial_ai_comment2

from ..url_patterns import URLS

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['detection']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'


import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성


class DetectionPostExtraContextMixin(BaseExtraContextMixin):
    """
    모든 뷰에서 공통적으로 사용할 추가 데이터를 템플릿 컨텍스트에 전달하는 Mixin입니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.
    """

    def get_context_data(self, **kwargs) -> dict:
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        게시판 이름 및 댓글 폼을 템플릿에 전달하여 사용할 수 있도록 설정합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자들입니다.

        Returns
        -------
        dict
            추가 데이터를 포함한 템플릿 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = DetectionCommentForm()  # 댓글 작성 폼 추가
        return context


class DetectionPostListView(DetectionPostExtraContextMixin, BaseListView):
    """
    DetectionPostListView 클래스는 특정 인물 찾기 게시판의 게시글 목록을 보여주는 뷰입니다.

    검색 기능을 제공하여 제목, 내용, 작성자 이름으로 검색할 수 있습니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
        
    search_fields : list
        검색할 필드를 지정합니다.
    """
    
    model = DetectionPostModel  # 사용할 모델 설정
    template_name = 'pybo/question_list.html'  # 사용할 템플릿 파일 설정
    search_fields = ['subject', 'content', 'author__username']  # 검색 가능한 필드 설정


class DetectionPostReadView(DetectionPostExtraContextMixin, BaseReadView):
    """
    DetectionPostReadView 클래스는 특정 인물 찾기 게시판의 게시글 상세 내용을 보여주는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """
    
    model = DetectionPostModel  # 사용할 모델 설정
    template_name = 'pybo/question_detail.html'  # 사용할 템플릿 파일 설정


class DetectionPostCreateView(DetectionPostExtraContextMixin, BaseCreateView):
    """
    DetectionPostCreateView 클래스는 특정 인물 찾기 게시판의 게시글을 작성하는 뷰입니다.

    AI 탐지기를 사용해 게시글을 생성 후, 추가적인 AI 처리 작업을 수행합니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    form_class : Form
        사용할 게시글 작성 폼 클래스입니다.
        
    success_url : str
        게시글 작성 후 이동할 URL입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.

    Methods
    -------
    form_valid(form):
        폼이 유효한 경우 AI 처리 로직을 실행하고 게시글을 저장합니다.
    """

    model = DetectionPostModel  # 사용할 모델 설정
    form_class = DetectionPostForm  # 게시글 작성 폼 클래스 설정
    success_url = read_url  # 게시글 작성 후 이동할 URL 설정
    template_name = 'pybo/question_form.html'  # 사용할 템플릿 파일 설정

    def form_valid(self, form):
        """
        폼이 유효한 경우 AI 처리 로직을 실행하고 게시글을 저장하는 메서드입니다.

        AI 탐지기와 예측기를 사용하여 게시글 작성 후, AI 처리를 실행합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            작성된 게시글의 상세 페이지로 리다이렉트됩니다.
        """
        response = super().form_valid(form)  # 상위 클래스의 form_valid() 호출

        post = form.instance  # 저장된 게시글 인스턴스 가져오기
        
        if post.image1:  # 이미지가 있는 경우에만 AI 처리
            logger.info(f"AI 처리 시작 - 게시글 ID: {post.id}")
            try:
                create_initial_ai_comment2(post_id=post.id)  # AI 처리 시작
                logger.info(f"AI 처리 완료 - 게시글 ID: {post.id}")
            except Exception as e:
                logger.error(f"AI 처리 실패 - 게시글 ID: {post.id}, 에러: {str(e)}")

        return response  # form_valid의 결과 반환


class DetectionPostUpdateView(DetectionPostExtraContextMixin, BaseUpdateView):
    """
    DetectionPostUpdateView 클래스는 특정 인물 찾기 게시판의 게시글을 수정하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    form_class : Form
        사용할 게시글 수정 폼 클래스입니다.
        
    success_url : str
        게시글 수정 후 이동할 URL입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """
    
    model = DetectionPostModel  # 사용할 모델 설정
    form_class = DetectionPostForm  # 게시글 수정 폼 클래스 설정
    success_url = read_url  # 게시글 수정 후 이동할 URL 설정
    template_name = 'pybo/question_form.html'  # 사용할 템플릿 파일 설정


class DetectionPostDeleteView(DetectionPostExtraContextMixin, BaseDeleteView):
    """
    DetectionPostDeleteView 클래스는 특정 인물 찾기 게시판의 게시글을 삭제하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    success_url : str
        게시글 삭제 후 이동할 URL입니다.
    """
    
    model = DetectionPostModel  # 사용할 모델 설정
    success_url = list_url  # 게시글 삭제 후 이동할 URL 설정


class DetectionPostVoteView(DetectionPostExtraContextMixin, BaseVoteView):
    """
    DetectionPostVoteView 클래스는 특정 인물 찾기 게시판의 게시글에 추천 기능을 제공하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    success_url : str
        추천 후 이동할 URL입니다.
    """
    
    model = DetectionPostModel  # 사용할 모델 설정
    success_url = read_url  # 추천 후 이동할 URL 설정
