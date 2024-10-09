from django.urls import reverse
from .base_views import BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import SimilarityComment, SimilarityPostModel
from ..forms import SimilarityCommentForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

import logging

from ..url_patterns import URLS

logger = logging.getLogger(URLS['APP_NAME'])

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['similarity']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

# 리다이렉트 URL 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'


class SimilarityCommentExtraContextMixin(BaseExtraContextMixin):

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['board_name'] = board_name  # 게시판 이름 설정
        context['comment_form'] = SimilarityCommentForm()  # 댓글 작성 폼 추가
        return context


class SimilarityCommentCreateView(SimilarityCommentExtraContextMixin, BaseCreateView):
    
    model = SimilarityComment  # 사용할 모델 설정
    form_class = SimilarityCommentForm  # 댓글 작성 폼 클래스 설정
    success_url = read_url  # 댓글 작성 후 이동할 URL 설정

    def form_valid(self, form):

        comment = form.instance  # 폼의 인스턴스를 가져옴
        comment.post = get_object_or_404(SimilarityPostModel, pk=self.kwargs['pk'])  # 게시글과 댓글 연결
        response = super().form_valid(form)  # 상위 클래스의 form_valid() 호출
        messages.success(self.request, '댓글이 성공적으로 작성되었습니다.', extra_tags='comment')  # 성공 메시지 표시
        return response  # 상위 클래스의 결과 반환


class SimilarityCommentUpdateView(BaseUpdateView):

    
    model = SimilarityComment  # 사용할 모델 설정
    form_class = SimilarityCommentForm  # 댓글 수정 폼 클래스 설정
    template_name = 'pybo/answer_form.html'  # 템플릿 경로 설정
    success_url = read_url  # 댓글 수정 후 이동할 URL 설정


class SimilarityCommentDeleteView(BaseDeleteView): 


    
    model = SimilarityComment  # 사용할 모델 설정
    success_url = read_url  # 댓글 삭제 후 이동할 URL 설정


class SimilarityCommentVoteView(BaseVoteView):

    model = SimilarityComment  # 사용할 모델 설정
    success_url = read_url  # 추천 후 이동할 URL 설정


from background_task import background

def create_initial_ai_comment(post_id: int) -> None:

    
    from django.contrib.auth.models import User
    from ..models import SimilarityPostModel, SimilarityComment

    logger.info(f"초기 AI 댓글 생성 - Board:{board_name} ID: {post_id}")

    post = get_object_or_404(SimilarityPostModel, pk=post_id)  # 게시글 조회

    try:
        # AI 계정 슈퍼유저 조회
        ai_user = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI가 작성한 초기 댓글 생성
    comment = SimilarityComment(
        author=ai_user,
        post=post,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    comment.save()

    # AI 백그라운드 작업 예약
    schedule_ai_comment_update(
        comment_id=comment.id,
        post_id=post_id,
        schedule=1  # 1초 후 실행 예약
    )

@background(schedule=1)
def schedule_ai_comment_update(comment_id: int, post_id: int) -> None:

    
    from ..models import SimilarityPostModel, SimilarityComment
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    import httpx
    import mimetypes
    import os
    import platform
    
    logger.info(f"AI 처리 중 - Board:{board_name} ID: {post_id}")

    # 댓글 및 게시글 조회
    comment = get_object_or_404(SimilarityComment, pk=comment_id)  # 댓글 조회
    post = get_object_or_404(SimilarityPostModel, pk=post_id)  # 게시글 조회

    # 이미지 경로 조회
    image1_path = post.image1.path  # 첫 번째 이미지 경로
    image2_path = post.image2.path  # 두 번째 이미지 경로

    # 이미지 타입 추정
    img1_type = mimetypes.guess_type(image1_path)
    img2_type = mimetypes.guess_type(image2_path)

    try:
        # 운영체제에 맞는 경로 처리 (특히 윈도우와 리눅스)
        if platform.system() == "Windows":
            image1_path = image1_path.replace("/", "\\")
            image2_path = image2_path.replace("/", "\\")
        else:
            image1_path = image1_path.replace("\\", "/")
            image2_path = image2_path.replace("\\", "/")

        # AI 서버로 이미지 전송 및 처리 결과 받기
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
                response = client.post(
                    "http://52.78.102.210:8007/process_ai_image_two/",
                    files={
                        'file1': (os.path.basename(image1_path), f1, img1_type[0]),
                        'file2': (os.path.basename(image2_path), f2, img2_type[0])
                    }
                )
        
        # 응답 처리
        if response.status_code == 200:
            result = response.json()

            # AI 처리 결과를 댓글에 저장
            comment.content = result.get('result', 'AI 처리 결과가 없습니다.')
            comment.save()

            logger.info(f"AI 처리 완료 - Board:{board_name} ID: {post_id}")

    except ValueError as e:
        # 얼굴 유사도 계산 중 문제가 발생했을 경우 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = str(e)  # 예외 메시지를 댓글 내용으로 저장
        comment.modify_date = timezone.now()  # 수정 날짜 업데이트
        comment.save()
        
    except Exception as e:
        # 기타 AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."  # 오류 메시지 저장
        comment.modify_date = timezone.now()  # 수정 날짜 업데이트
        comment.save()
