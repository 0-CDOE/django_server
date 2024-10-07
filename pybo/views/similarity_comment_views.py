from django.urls import reverse
from .base_views import BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView, BaseExtraContextMixin
from ..models import SimilarityComment, SimilarityPost
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

# 리다이렉트 url 설정
read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'

class ExtraContextMixin(BaseExtraContextMixin):
    """
    모든 뷰에서 공통적으로 사용할 context 데이터를 추가하는 Mixin
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['board_name'] = board_name
        context['comment_form'] = SimilarityCommentForm() # 질문 상세보기 페이지에 댓글 폼을 추가하기 위해 폼 객체를 컨텍스트에 추가
        return context

# ==============================
# Similarity Comment Views
# ==============================

class SimilarityCommentCreateView(ExtraContextMixin, BaseCreateView):
    """
    얼굴 유사도 비교 게시판의 댓글 생성 뷰.
    """
    model = SimilarityComment
    form_class = SimilarityCommentForm
    success_url = read_url

    def form_valid(self, form):
        
        comment = form.instance
        comment.post = get_object_or_404(SimilarityPost, pk=self.kwargs['pk'])
        
        # 여기서 부터 상위 클래스의 form_valid() 메서드 이어쓰기 실행
        # 여기 부분에 상위 클래스의 form_valid() 메서드가 실행된다. 흐름을 잘 이해하자.
        response = super().form_valid(form) 
        messages.success(self.request, '댓글이 성공적으로 작성되었습니다.', extra_tags='comment')
        
        # 상위 클래스의 결과를 반환
        return response


class SimilarityCommentUpdateView(BaseUpdateView):
    """
    얼굴 유사도 비교 게시판의 댓글 수정 뷰.
    """
    model = SimilarityComment
    form_class = SimilarityCommentForm
    template_name = 'pybo/answer_form.html'
    success_url = read_url

class SimilarityCommentDeleteView(BaseDeleteView): 
    """
    얼굴 유사도 비교 게시판의 댓글 삭제 뷰.
    """
    model = SimilarityComment
    success_url = read_url  # 삭제 후 이동할 URL


class SimilarityCommentVoteView(BaseVoteView):
    
    model = SimilarityComment
    success_url = read_url


# ===============================================
# AI 관련 백그라운드 처리 함수
# ===============================================
from background_task import background


def create_initial_ai_comment(post_id):
    """
    AI 처리 중임을 알리는 초기 답변을 생성하는 함수.
    'AI' 사용자 계정이 답변 작성자로 설정되며, 백그라운드에서 AI 처리를 예약한다.
    
    Args:
        question_id (int): 질문의 ID.
        selected_detectors (list): 선택된 AI 탐지기 목록.
        selected_predictors (list): 선택된 AI 예측기 목록.
    """
    
    from django.contrib.auth.models import User
    from ..models import SimilarityPost, SimilarityComment

    logger.info(f"초기 답변 생성 Q: {post_id}")

    # 질문 객체를 조회
    post = get_object_or_404(SimilarityPost, pk=post_id)

    try:
        # AI 계정 슈퍼유저 조회
        ai_user = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI가 작성한 초기 답변 생성
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
        question_id=post_id,
        schedule=1  # 1초 후 실행 예약
    )


@background(schedule=1)
def schedule_ai_comment_update(comment_id, question_id):
    """
    백그라운드에서 AI 처리를 실행하고, 처리 결과를 답변으로 업데이트하는 함수.
    
    Args:
        answer_id (int): 답변의 ID.
        question_id (int): 질문의 ID.
        selected_detectors (list): 선택된 AI 탐지기 목록.
        selected_predictors (list): 선택된 AI 예측기 목록.
    """
    
    from ..models import SimilarityPost, SimilarityComment
    from .ai import compare_faces

    logger.info(f"AI 처리 중 Q: {question_id}")

    # 답변 및 질문 객체 조회
    comment = get_object_or_404(SimilarityComment, pk=comment_id)
    post = get_object_or_404(SimilarityPost, pk=question_id)
    
    image1_path = post.image1.path # 이미지1 경로  
    image2_path = post.image2.path # 이미지2 경로  

    try:
        # AI로 이미지 처리 후 결과 이미지 경로 저장
        similarity_percent = compare_faces(image1_path, image2_path)
        comment.content = f"""
당신의 얼굴은 **도널드 트럼프**와 **{similarity_percent:.2f}%**만큼 유사합니다!

트럼프는 강력한 리더십과 자신감을 상징하는 인물로, 중요한 순간마다 결단력을 보여주었습니다.  
당신도 이러한 유사성을 통해 **리더십**과 **결단력**이라는 중요한 특성을 공유하고 있을 가능성이 큽니다. 

이 유사성은 단순한 외모를 넘어서, 당신이 가진 독창적이고 강한 의지를 반영하는 부분입니다.  
트럼프처럼 도전에 맞서고 목표를 위해 나아가는 모습에서 공통점을 찾을 수 있습니다.
"""


        comment.save()

        logger.info(f"AI 처리 완료 A: {comment.id}")

    except Exception as e:
        # AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 Q: {question_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()
        comment.save()
