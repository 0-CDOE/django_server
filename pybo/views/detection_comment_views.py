from .base_views import BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import DetectionComment, DetectionPost
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

# 리다이렉트 url 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'


class DCommentECMixin(BaseExtraContextMixin):
    """
    모든 뷰에서 공통적으로 사용할 context 데이터를 추가하는 Mixin
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board_name'] = board_name
        context['comment_form'] = DetectionCommentForm()  # 게시글 상세보기 페이지에 댓글 폼을 추가
        return context



class DetectionCommentCreateView(DCommentECMixin, BaseCreateView):
    """
    특정 인물 찾기 게시판의 댓글 생성 뷰.
    """

    model = DetectionComment
    form_class = DetectionCommentForm
    success_url = read_url

    def form_valid(self, form):
        comment = form.instance
        comment.post = get_object_or_404(DetectionPost, pk=self.kwargs['pk'])

        response = super().form_valid(form)
        messages.success(self.request, '댓글이 성공적으로 작성되었습니다.', extra_tags='comment')

        return response


class DetectionCommentUpdateView(BaseUpdateView):
    """
    특정 인물 찾기 게시판의 댓글 수정 뷰.
    """

    model = DetectionComment
    form_class = DetectionCommentForm
    template_name = 'pybo/answer_form.html'
    success_url = read_url


class DetectionCommentDeleteView(BaseDeleteView):
    """
    특정 인물 찾기 게시판의 댓글 삭제 뷰.
    """

    model = DetectionComment
    success_url = read_url  # 삭제 후 이동할 URL


class DetectionCommentVoteView(BaseVoteView):
    """
    특정 인물 찾기 게시판의 댓글 추천 뷰.
    """

    model = DetectionComment
    success_url = read_url


# ===============================================
# AI 관련 백그라운드 처리 함수
# ===============================================
from background_task import background


def create_initial_ai_answer2(post_id):
    """
    AI 처리 중임을 알리는 초기 답변을 생성하는 함수.
    'AI' 사용자 계정이 답변 작성자로 설정되며, 백그라운드에서 AI 처리를 예약한다.
    """

    from django.contrib.auth.models import User
    from ..models import DetectionPost, DetectionComment

    logger.info(f"초기 답변 생성 Q: {post_id}")

    post = get_object_or_404(DetectionPost, pk=post_id)

    try:
        ai_user = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    comment = DetectionComment(
        author=ai_user,
        post=post,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    comment.save()

    schedule_ai_comment_update2(
        comment_id=comment.id,
        question_id=post_id,
        schedule=1  # 1초 후 실행 예약
    )


@background(schedule=1)
def schedule_ai_comment_update2(comment_id, question_id):
    """
    백그라운드에서 AI 처리를 실행하고, 처리 결과를 답변으로 업데이트하는 함수.
    """

    from ..models import DetectionPost, DetectionComment
    from .ai import process_image2

    logger.info(f"AI 처리 중 Q: {question_id}")

    comment = get_object_or_404(DetectionComment, pk=comment_id)
    post = get_object_or_404(DetectionPost, pk=question_id)

    image_path = post.image1.path  # 게시글에 첨부된 이미지 경로 조회

    try:
        result_image_path = process_image2(image_path)
        comment.content = "이 사진 속 인물은 도널드 트럼프(Donald Trump)입니다. 그는 미국의 제45대 대통령으로 2017년부터 2021년까지 재임했으며, 정치인이기 이전에는 부동산 개발업자이자 TV 방송인으로도 유명했습니다. 트럼프는 2016년 대통령 선거에서 공화당 후보로 출마해 승리했으며, 재임 중에는 ‘미국 우선주의’를 내세워 보호무역, 이민 제한, 세금 감면 등의 정책을 추진했습니다."
        comment.image1 = result_image_path
        comment.save()

        logger.info(f"AI 처리 완료 A: {comment.id}")

    except Exception as e:
        logger.exception(f"AI 처리 실패 Q: {question_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()
        comment.save()
