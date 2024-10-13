from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .base_views import BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionCommentModel, DetectionPostModel
from ..forms import DetectionCommentForm
from ..url_patterns import URLS

import logging
logger = logging.getLogger(URLS['APP_NAME'])

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['detection']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'

# base_views 에서 설정 못한 클래스 변수 설정
# 댓글 모델, 댓글 폼, 게시글 모델 설정
comment_model = DetectionCommentModel
comment_form = DetectionCommentForm
post_model = DetectionPostModel

# 탬플릿 설정
comment_form_template = f'{app_name}/answer_form.html'

class DetectionExtraContextMixin(BaseExtraContextMixin):
    """
    모든 댓글 관련 뷰에서 공통적으로 사용할 추가 데이터를 설정하는 Mixin입니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 전달할 추가 데이터를 설정합니다.

    Returns
    -------
    dict
        템플릿에 전달할 추가 데이터를 포함한 컨텍스트 딕셔너리입니다.
    """

    def get_context_data(self, **kwargs) -> dict:
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        게시판 이름과 댓글 작성 폼을 템플릿에 추가합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자들입니다.

        Returns
        -------
        dict
            추가 데이터를 포함한 템플릿 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스 메서드 호출
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = comment_form()  # 댓글 작성 폼 추가
        return context


class DetectionCommentCreateView(DetectionExtraContextMixin, BaseCreateView):
    """
    특정 인물 찾기 게시판의 댓글을 작성하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 댓글 모델(DetectionComment)입니다.
        
    form_class : Form
        사용할 댓글 작성 폼 클래스입니다.
        
    success_url : str
        댓글 작성 후 이동할 URL입니다.

    Methods
    -------
    form_valid(form):
        폼이 유효한 경우 댓글을 작성하고 저장합니다.
    """
    
    model = comment_model  # 사용할 댓글 모델 설정
    form_class = comment_form  # 댓글 작성 폼 클래스 설정
    success_url = read_url  # 댓글 작성 후 이동할 URL 설정

    def form_valid(self, form):
        """
        폼이 유효할 경우 댓글을 작성하고 저장하는 메서드입니다.

        작성된 댓글은 해당 게시글과 연결됩니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 댓글 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            작성된 댓글이 포함된 게시글 상세 페이지로 리다이렉트됩니다.
        """
        comment = form.instance  # 폼 인스턴스에서 댓글 객체 가져오기
        comment.post = get_object_or_404(post_model, pk=self.kwargs['pk'])  # 댓글이 달릴 게시글 찾기

        response = super().form_valid(form)  # 상위 클래스의 form_valid 호출
        messages.success(self.request, '댓글이 성공적으로 작성되었습니다.', extra_tags='comment')  # 성공 메시지 표시

        return response  # 상위 클래스의 결과 반환


class DetectionCommentUpdateView(BaseUpdateView):
    """
    특정 인물 찾기 게시판의 댓글을 수정하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 댓글 모델(DetectionComment)입니다.
        
    form_class : Form
        사용할 댓글 수정 폼 클래스입니다.
        
    template_name : str
        사용할 템플릿 파일 경로입니다.
        
    success_url : str
        댓글 수정 후 이동할 URL입니다.
    """
    
    model = comment_model  # 사용할 댓글 모델 설정
    form_class = comment_form  # 댓글 수정 폼 클래스 설정
    template_name = comment_form_template  # 사용할 템플릿 파일 경로 설정
    success_url = read_url  # 댓글 수정 후 이동할 URL 설정


class DetectionCommentDeleteView(BaseDeleteView):
    """
    특정 인물 찾기 게시판의 댓글을 삭제하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 댓글 모델(DetectionComment)입니다.
        
    success_url : str
        댓글 삭제 후 이동할 URL입니다.
    """
    
    model = comment_model  # 사용할 댓글 모델 설정
    success_url = read_url  # 댓글 삭제 후 이동할 URL 설정


class DetectionCommentVoteView(BaseVoteView):
    """
    특정 인물 찾기 게시판의 댓글 추천 기능을 제공하는 뷰입니다.

    Attributes
    ----------
    model : Model
        사용할 댓글 모델(DetectionComment)입니다.
        
    success_url : str
        추천 후 이동할 URL입니다.
    """
    
    model = comment_model  # 사용할 댓글 모델 설정
    success_url = read_url  # 추천 후 이동할 URL 설정

