from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 상태 확인을 위한 믹스인
from django.shortcuts import get_object_or_404, redirect  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티
from django.views.generic import CreateView, UpdateView, DeleteView, RedirectView  # 제네릭 뷰 사용
from django.urls import reverse, reverse_lazy  # URL 처리

# 필요한 모델과 폼 임포트
from ..models import SimilarityPost, SimilarityComment
from ..forms import AnswerForm

from ..url_patterns import URLS

import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 객체 생성

class AnswerFormMixin:
    """
    답변 생성 및 수정 폼 처리를 위한 믹스인 클래스.
    질문 객체를 가져오고, 폼이 유효할 때 데이터를 저장하는 로직을 포함한다.
    
    Attributes:
        model (Model): Answer 모델을 사용.
        form_class (Form): AnswerForm을 사용하여 폼을 처리.
        template_name (str): 폼의 HTML 템플릿을 지정.
    """
    
    model = SimilarityComment
    form_class = AnswerForm
    template_name = 'pybo/answer_form.html'

    def form_valid(self, form):
        """
        폼이 유효할 경우 답변을 저장하고, 해당 질문의 상세 페이지로 리다이렉트한다.
        
        Args:
            form: 유효성 검증을 통과한 폼 데이터.
        
        Returns:
            redirect: 질문 상세 페이지로 리다이렉트.
        """

        
        answer = form.save(commit=False)  # 답변 객체 저장, 나중에 DB에 저장

        # 답변이 새로 생성되는 경우 (ID가 없는 경우)
        if not answer.id:
            question = get_object_or_404(SimilarityPost, pk=self.kwargs['pk'])
            answer.author = self.request.user
            answer.create_date = timezone.now()
            answer.question = question
        else:
            answer.modify_date = timezone.now()  # 답변 수정 시간을 설정

        answer.save()  # 답변을 DB에 저장

        # 질문의 상세 페이지로 리다이렉트
        return redirect(reverse(question_detail_url, kwargs={'pk': answer.question_id}))


class AnswerCreateView(LoginRequiredMixin, AnswerFormMixin, CreateView):
    """
    답변 생성 뷰.
    로그인한 사용자만 접근할 수 있으며, AnswerFormMixin을 사용하여 폼 처리를 한다.
    """
    pass


class AnswerUpdateView(LoginRequiredMixin, AnswerFormMixin, UpdateView):
    """
    답변 수정 뷰.
    로그인한 사용자만 접근할 수 있으며, AnswerFormMixin을 사용하여 폼 처리를 한다.
    UpdateView 내부에는 get 메서드와 post 메서드가 있어 기존 답변을 가져오고 수정한다.
    이 점이 CreateView와 다르다.
    """
    pass


class AnswerDeleteView(LoginRequiredMixin, DeleteView):
    """
    답변 삭제 뷰.
    로그인한 사용자만 답변을 삭제할 수 있으며, 삭제 후 질문 상세 페이지로 리다이렉트한다.
    """
    
    model = SimilarityComment

    def get(self, request, *args, **kwargs):
        """
        GET 요청 시 삭제 처리.
        
        Args:
            request: HTTP 요청 객체.
        
        Returns:
            HttpResponse: 답변 삭제 후 질문 상세 페이지로 리다이렉트.
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        답변 삭제 처리.
        답변 작성자가 아니면 에러 메시지를 출력하고, 질문 상세 페이지로 리다이렉트한다.
        
        Args:
            request: 삭제 요청.
        
        Returns:
            redirect: 질문 상세 페이지로 리다이렉트.
        """
        
             

        answer = self.get_object()
        
        # 삭제 권한이 없는 경우 에러 메시지 출력
        if request.user != answer.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect(question_detail_url, pk=answer.question.pk)

        # 답변 삭제 처리
        answer.delete()

        # 질문 상세 페이지로 리다이렉트
        return redirect(reverse_lazy(question_detail_url, kwargs={'pk': answer.question.id}))



class AnswerVoteView(LoginRequiredMixin, RedirectView):
    """
    답변 추천 기능을 처리하는 제네릭 뷰.
    로그인한 사용자는 답변을 추천할 수 있으며, 본인의 답변은 추천할 수 없다.
    """

    permanent = False  # 임시 리다이렉트
    query_string = True  # 쿼리 스트링을 사용할 수 있게 설정

    def get_redirect_url(self, *args, **kwargs):
        """
        추천 처리 후 리다이렉트할 URL을 반환한다.
        
        Args:
            *args: 추가 인자.
            **kwargs: URL 패턴에 필요한 매개변수.

        Returns:
            str: 리다이렉트할 URL.
        """
        answer = get_object_or_404(SimilarityComment, pk=kwargs['pk'])

        # 추천 불가 조건 처리
        if self.request.user == answer.author:
            messages.error(self.request, '본인이 작성한 답변은 추천할 수 없습니다.')
        elif self.request.user in answer.voter.all():
            messages.error(self.request, '이미 추천한 답변입니다.')
        else:
            answer.voter.add(self.request.user)
            messages.success(self.request, '답변을 추천했습니다.')

        # 질문 상세 페이지로 리다이렉트 후 해당 답변으로 이동
        return '{}#answer_{}'.format(reverse(question_detail_url, kwargs={'pk': answer.post.pk}), answer.pk)


# ===============================================
# AI 관련 백그라운드 처리 함수
# ===============================================
from background_task import background


def create_initial_ai_answer(question_id, selected_detectors, selected_predictors):
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

    logger.info(f"초기 답변 생성 Q: {question_id}")

    # 질문 객체를 조회
    question = get_object_or_404(SimilarityPost, pk=question_id)

    try:
        # AI 계정 슈퍼유저 조회
        ai_user = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI가 작성한 초기 답변 생성
    answer = SimilarityComment(
        author=ai_user,
        question=question,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    answer.save()

    # AI 백그라운드 작업 예약
    schedule_ai_answer_update(
        answer_id=answer.id,
        question_id=question_id,
        selected_detectors=selected_detectors,
        selected_predictors=selected_predictors,
        schedule=1  # 1초 후 실행 예약
    )


@background(schedule=1)
def schedule_ai_answer_update(answer_id, question_id, selected_detectors, selected_predictors):
    """
    백그라운드에서 AI 처리를 실행하고, 처리 결과를 답변으로 업데이트하는 함수.
    
    Args:
        answer_id (int): 답변의 ID.
        question_id (int): 질문의 ID.
        selected_detectors (list): 선택된 AI 탐지기 목록.
        selected_predictors (list): 선택된 AI 예측기 목록.
    """
    
    from ..models import SimilarityPost, SimilarityComment
    from .ai import process_image

    logger.info(f"AI 처리 중 Q: {question_id}")

    # 답변 및 질문 객체 조회
    answer = get_object_or_404(SimilarityComment, pk=answer_id)
    question = get_object_or_404(SimilarityPost, pk=question_id)
    
    image_path = question.image1.path  # 질문에 첨부된 이미지 경로 조회

    try:
        # AI로 이미지 처리 후 결과 이미지 경로 저장
        result_image_path = process_image(image_path, selected_detectors, selected_predictors)
        answer.content = "AI가 처리한 얼굴 인식 결과입니다."
        answer.answer_image = result_image_path
        answer.save()

        logger.info(f"AI 처리 완료 A: {answer.id}")

    except Exception as e:
        # AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 Q: {question_id}")
        answer.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        answer.modify_date = timezone.now()
        answer.save()
