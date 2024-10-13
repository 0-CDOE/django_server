from django.contrib import messages

from .base_views import BaseListView, BaseReadView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionPostModel, DetectionCommentModel
from ..forms import DetectionPostForm, DetectionCommentForm
from ..url_patterns import URLS
from ..services.ai_comment_service import AICommentService

import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['detection']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'

# base_views 에서 설정 못한 클래스 변수 설정
# 댓글 모델, 댓글 폼, 게시글 모델 설정
post_model = DetectionPostModel
post_form = DetectionPostForm
comment_form = DetectionCommentForm
comment_model = DetectionCommentModel

# 탬플릿 설정
post_list_template = f'{app_name}/question_list.html'
post_form_template = f'{app_name}/question_form.html'
post_read_template = f'{app_name}/question_detail.html'


class DetectionExtraContextMixin(BaseExtraContextMixin):
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
        context['comment_form'] = comment_form()  # 댓글 작성 폼 추가
        return context


class DetectionPostListView(DetectionExtraContextMixin, BaseListView):
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
    
    model = post_model  # 사용할 모델 설정
    template_name = post_list_template  # 사용할 템플릿 파일 설정
    search_fields = ['subject', 'content', 'author__username']  # 검색 가능한 필드 설정


class DetectionPostReadView(DetectionExtraContextMixin, BaseReadView):
    """
    DetectionPostReadView 클래스는 특정 인물 찾기 게시판의 게시글 상세 내용을 보여주는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
    """
    
    model = post_model  # 사용할 모델 설정
    template_name = post_read_template  # 사용할 템플릿 파일 설정


class DetectionPostCreateView(DetectionExtraContextMixin, BaseCreateView):
    """
    DetectionPostCreateView 클래스는 특정 인물 찾기 게시판에서 게시글을 작성하는 뷰입니다.
    이 클래스는 게시글을 저장한 후, AI 기반 탐지 작업을 통해 게시글의 이미지를 처리하고 
    AI가 자동으로 댓글을 달 수 있도록 합니다.

    Attributes
    ----------
    model : django.db.models.Model
        게시글에 사용할 Django 모델입니다. 이 모델은 게시글을 데이터베이스에 저장합니다.

    form_class : django.forms.ModelForm
        사용자가 게시글을 작성할 때 사용할 폼 클래스입니다. 이 폼은 사용자가 입력한 데이터를 
        게시글 모델로 변환하는 데 사용됩니다.

    success_url : str
        게시글 작성이 완료된 후, 리다이렉트할 URL을 나타냅니다. 작성된 게시글의 상세 페이지로 이동합니다.

    template_name : str
        사용자가 게시글을 작성할 때 보여줄 HTML 템플릿의 경로입니다.

    Methods
    -------
    form_valid(form: django.forms.ModelForm) -> django.http.HttpResponseRedirect
        폼이 유효한 경우 AI 처리 로직을 실행하고, 게시글을 저장한 후 리다이렉트합니다.
    """

    model = post_model  # 게시글에 사용할 모델 (DetectionPostModel)
    form_class = post_form  # 게시글 작성 폼 클래스
    success_url = read_url  # 작성 완료 후 이동할 URL
    template_name = post_form_template  # 사용할 템플릿 파일 경로

    def form_valid(self, form: post_form):
        """
        form_valid 메서드는 폼이 유효한 경우 호출되며, AI 기반 처리 로직을 실행하고 게시글을 저장합니다.
        
        이 메서드는 게시글을 저장한 후, 저장된 게시글에 포함된 이미지를 AI가 처리하여 
        자동으로 댓글을 생성하는 작업을 수행합니다.

        Parameters
        ----------
        form : post_form
            사용자가 작성한 게시글 데이터를 포함하는 폼 인스턴스입니다. 이 폼은 게시글 모델로 변환되며,
            폼 유효성 검사를 통과한 데이터가 포함됩니다.

        Returns
        -------
        HttpResponseRedirect
            게시글이 성공적으로 작성된 후, 작성된 게시글의 상세 페이지로 리다이렉트됩니다.
        """
        # 상위 클래스(BaseCreateView)의 form_valid 메서드를 호출하여 게시글을 저장
        response = super().form_valid(form)  
        
        # 저장된 게시글 인스턴스를 가져오기
        post = form.instance  
        
        # 게시글에 이미지가 있는 경우에만 AI 처리를 시작
        if post.image1:  
            logger.info(f"AI 처리 시작 - 게시글 ID: {post.id}")
            try:
                # AI 댓글 생성 서비스를 호출하여 게시글에 AI 댓글 생성 작업 실행
                ai_comment_service = AICommentService(post, comment_model, board_name)
                
                # AI 댓글 생성 후 성공 여부를 확인
                ai_comment_service.create_comment()

                # AI가 특정 인물을 찾는 작업을 추가로 실행
                ai_comment_service.detect_president()

            except Exception as e:
                # 예외 발생 시 로그에 오류 메시지 기록
                logger.error(f"AI 처리 실패 - 게시글 ID: {post.id}, 에러: {str(e)}")
        
        # form_valid의 기본 결과 반환 (게시글 상세 페이지로 리다이렉트)
        return response


class DetectionPostUpdateView(DetectionExtraContextMixin, BaseUpdateView):
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
    
    model = post_model  # 사용할 모델 설정
    form_class = post_form  # 게시글 수정 폼 클래스 설정
    success_url = read_url  # 게시글 수정 후 이동할 URL 설정
    template_name = post_form_template  # 사용할 템플릿 파일 설정


class DetectionPostDeleteView(BaseDeleteView):
    """
    DetectionPostDeleteView 클래스는 특정 인물 찾기 게시판의 게시글을 삭제하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    success_url : str
        게시글 삭제 후 이동할 URL입니다.
    """
    
    model = post_model  # 사용할 모델 설정
    success_url = list_url  # 게시글 삭제 후 이동할 URL 설정


class DetectionPostVoteView(BaseVoteView):
    """
    DetectionPostVoteView 클래스는 특정 인물 찾기 게시판의 게시글에 추천 기능을 제공하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 게시글 모델입니다.
        
    success_url : str
        추천 후 이동할 URL입니다.
    """
    
    model = post_model  # 사용할 모델 설정
    success_url = read_url  # 추천 후 이동할 URL 설정


