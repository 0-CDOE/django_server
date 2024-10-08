from .base_views import BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionCommentModel, DetectionPostModel
from ..forms import DetectionCommentForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

import logging

from ..url_patterns import URLS

logger = logging.getLogger(URLS['APP_NAME'])

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['detection']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'


class DetectionCommentExtraContextMixin(BaseExtraContextMixin):
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
        context['comment_form'] = DetectionCommentForm()  # 댓글 작성 폼 추가
        return context


class DetectionCommentCreateView(DetectionCommentExtraContextMixin, BaseCreateView):
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
    
    model = DetectionCommentModel  # 사용할 댓글 모델 설정
    form_class = DetectionCommentForm  # 댓글 작성 폼 클래스 설정
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
        comment.post = get_object_or_404(DetectionPostModel, pk=self.kwargs['pk'])  # 댓글이 달릴 게시글 찾기

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
    
    model = DetectionCommentModel  # 사용할 댓글 모델 설정
    form_class = DetectionCommentForm  # 댓글 수정 폼 클래스 설정
    template_name = 'pybo/answer_form.html'  # 사용할 템플릿 파일 경로 설정
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
    
    model = DetectionCommentModel  # 사용할 댓글 모델 설정
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
    
    model = DetectionCommentModel  # 사용할 댓글 모델 설정
    success_url = read_url  # 추천 후 이동할 URL 설정


from background_task import background


def create_initial_ai_comment2(post_id: int) -> None:
    """
    AI 처리 중임을 알리는 초기 답변을 생성하는 함수입니다.

    AI 계정이 작성자로 설정되며, 이후 백그라운드 작업에서 AI 처리를 실행합니다.

    Parameters
    ----------
    post_id : int
        답변이 달릴 게시글의 ID입니다.

    Returns
    -------
    None
    """
    
    from django.contrib.auth.models import User
    from ..models import DetectionPostModel, DetectionCommentModel

    logger.info(f"초기 AI 답변 생성 - Board:{board_name} ID: {post_id}")

    post = get_object_or_404(DetectionPostModel, pk=post_id)  # 게시글 조회

    try:
        ai_user = User.objects.get(username='AI')  # AI 사용자 계정 조회
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI가 작성한 초기 답변 생성
    comment = DetectionCommentModel(
        author=ai_user,
        post=post,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    comment.save()

    # AI 백그라운드 작업 예약
    detect_president(
        comment_id=comment.id,
        post_id=post_id,
        schedule=1  # 1초 후 실행 예약
    )



@background(schedule=1)
def detect_president(comment_id: int, post_id: int) -> None:
    
    from ..models import DetectionPostModel, DetectionCommentModel
    import httpx
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    import os
    from django.conf import settings
    import base64
    import platform
    

    logger.info(f"AI 처리 중 - Board:{board_name} ID: {post_id}")

    comment = get_object_or_404(DetectionCommentModel, pk=comment_id)  # 댓글 조회
    post = get_object_or_404(DetectionPostModel, pk=post_id)  # 게시글 조회

    image_path = post.image1.path  # 게시글에 첨부된 이미지 경로 조회

    try:
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = client.post("http://52.78.102.210:8007/process_ai_image/", files=files)

        django_dir = settings.BASE_DIR

        if response.status_code == 200:  # OK
            data = response.json()

            # 서버에서 받은 경로 처리
            str_path = data['image_path']

            # 윈도우와 우분투를 모두 고려한 경로 처리
            if platform.system() == "Windows":
                # 윈도우일 경우
                result_image_path = os.path.join('media', str_path.split('media\\', 1)[-1])
                db_path = str_path.split('media\\', 1)[-1]
            else:
                # 우분투일 경우
                result_image_path = os.path.join('media', str_path.split('media/', 1)[-1])
                db_path = str_path.split('media/', 1)[-1]

            # 받은 이미지를 디코딩 후 저장
            result_image = data['base64_image']
            result_text = data['message']

            decode_image = base64.b64decode(result_image)
            results_folder = os.path.join(django_dir, result_image_path)

            with open(results_folder, 'wb') as out_file:
                out_file.write(decode_image)

            # AI로 이미지 처리 후 결과 이미지 경로 저장
            comment.content = result_text
            comment.image1 = db_path  # 처리된 이미지 경로 저장
            comment.save()

            logger.info(f"AI 처리 완료 - Board:{board_name} ID: {post_id}")
            
        else:
            comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
            
        comment.modify_date = timezone.now()  # 댓글 수정 날짜 갱신
        comment.save()
        
    except Exception as e:
        # AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()  # 댓글 수정 날짜 갱신
        comment.save()
