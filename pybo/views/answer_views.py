from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 필요를 확인하는 믹스인
from django.shortcuts import get_object_or_404, redirect  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티 모듈
from django.views.generic import CreateView, UpdateView, DeleteView  # 제네릭 뷰 사용
from django.urls import reverse, reverse_lazy  # URL 처리를 위한 모듈
from django.contrib.auth.decorators import login_required

import logging  # 로그 출력을 위한 모듈

# 로깅 설정
logger = logging.getLogger('pybo')

# 필요한 모델과 폼 임포트
from ..models import Question, Answer  # Question과 Answer 모델
from ..forms import AnswerForm  # AnswerForm 폼


class AnswerFormMixin:
    def form_valid(self, form):
        answer = form.save(commit=False)
        answer.author = self.request.user
        answer.create_date = timezone.now()
        answer.question = get_object_or_404(Question, pk=self.kwargs['pk'])
        answer.save()
        return redirect(reverse('pybo:detail', kwargs={'pk': answer.question.pk}))

class AnswerCreateView(LoginRequiredMixin, AnswerFormMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'pybo/question_detail.html'

class AnswerUpdateView(LoginRequiredMixin, AnswerFormMixin, UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'pybo/answer_form.html'

class AnswerDeleteView(LoginRequiredMixin, DeleteView):
    """
    답변 삭제 뷰
    사용자가 자신의 답변을 삭제하면,
    확인 페이지 없이 즉시 삭제하고 질문 상세 페이지로 리다이렉트합니다.
    """
    model = Answer  # 삭제할 모델을 설정

    def get_success_url(self):
        """
        삭제 후 질문 상세 페이지로 리다이렉트
        """
        answer = self.get_object()
        return reverse_lazy('pybo:detail', kwargs={'pk': answer.question.pk})

    def delete(self, request, *args, **kwargs):
        """
        POST 요청을 처리하여 답변을 삭제하고 질문 상세 페이지로 리다이렉트합니다.
        만약 사용자가 작성자가 아닐 경우, 에러 메시지를 출력합니다.
        """
        answer = self.get_object()
        if request.user != answer.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('pybo:detail', pk=answer.question.pk)

        answer.delete()
        return redirect(self.get_success_url())

@login_required
def answer_vote(request, pk):
    """
    답변 추천 처리 함수 뷰
    로그인한 사용자가 자신의 답변이 아닌 다른 답변을 추천할 수 있습니다.
    """
    # 추천할 답변 객체를 가져옴
    answer = get_object_or_404(Answer, pk=pk)

    # 작성자가 자신의 답변을 추천하지 못하게 처리
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    else:
        # 답변 추천 처리
        answer.voter.add(request.user)

    # 질문 상세 페이지로 리다이렉트
    return redirect('pybo:detail', pk=answer.question.pk)


# ===============================================
# AI 관련 백그라운드 처리 함수
# ===============================================
from background_task import background

def create_initial_ai_answer(question_id, user_id, selected_detectors, selected_predictors):
    """
    AI 처리 중인 상태로 초기 답변 생성.
    AI 작업이 시작되었음을 알리는 답변을 우선 생성합니다.
    """
    from django.contrib.auth.models import User  # User 모델을 가져옴
    from ..models import Question, Answer  # Question과 Answer 모델 가져오기

    logger.info(f"초기 답변 생성 Q: {question_id}")  # 로그 기록

    # 질문 객체 가져오기
    question = Question.objects.get(pk=question_id)

    # 'AI' 슈퍼유저 가져오기
    try:
        ai_superuser = User.objects.get(username='AI')  # AI 슈퍼유저를 가져옴
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI 처리 중임을 알리는 답변 생성
    answer = Answer(
        author=ai_superuser,  # 작성자를 'AI'로 설정
        question=question,
        content="AI가 처리 중입니다.",  # 메시지 설정
        create_date=timezone.now(),  # 작성 시간 설정
    )
    answer.save()  # 답변을 저장

    # 백그라운드 작업 예약
    ai_answer_update_background(
        answer_id=answer.id,
        question_id=question_id,
        selected_detectors=selected_detectors,
        selected_predictors=selected_predictors
    )

@background(schedule=1)
def ai_answer_update_background(answer_id, question_id, selected_detectors, selected_predictors):
    """
    백그라운드에서 AI 처리를 실행하고 답변을 업데이트.
    """
    from ..models import Question, Answer  # 모델 가져오기
    from .ai import process_image  # AI 이미지 처리 함수

    logger.info(f"AI 처리 중 Q: {question_id}")  # 로그 기록

    # 질문과 답변 객체 가져오기
    question = Question.objects.get(pk=question_id)
    answer = Answer.objects.get(pk=answer_id)

    # 업로드된 이미지 경로 가져오기
    image_path = question.image1.path

    try:
        # AI 처리 호출
        result_image_path = process_image(image_path, selected_detectors, selected_predictors)

        # AI 처리 후 답변 업데이트
        answer.content = "AI가 처리한 얼굴 인식 결과입니다."
        answer.answer_image = result_image_path
        answer.save()

        logger.info(f"AI 처리 완료 A: {answer.id}")  # 완료 로그 기록

    except Exception as e:
        # AI 처리 실패 시 예외 처리
        logger.error(f"AI 처리 실패 Q: {question_id}, Error: {str(e)}")
        answer.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        answer.modify_date = timezone.now()
        answer.save()

# ===============================================
