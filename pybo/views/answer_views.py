from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger('pybo')

from ..models import Question, Answer
from ..forms import AnswerForm


class AnswerFormMixin:
    def get_question(self):
        """
        질문 객체를 가져오는 헬퍼 메서드
        """
        return get_object_or_404(Question, pk=self.kwargs['pk'])

    def form_valid(self, form):
        """
        폼이 유효할 때 처리 로직을 포함한 메서드
        """
        answer = form.save(commit=False)
        answer.author = self.request.user
        answer.create_date = timezone.now()
        answer.question = self.get_question()
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
    model = Answer

    def dispatch(self, request, *args, **kwargs):
        answer = self.get_object()
        if request.user != answer.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('pybo:detail', pk=answer.question.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        dispatch에서 이미 answer를 가져왔으므로 이를 재사용
        """
        return reverse_lazy('pybo:detail', kwargs={'pk': self.get_object().question.pk})



@login_required
def answer_vote(request, pk):
    """
    답변 추천 기능 처리
    """
    answer = get_object_or_404(Answer, pk=pk)
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    else:
        answer.voter.add(request.user)
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
    from django.contrib.auth.models import User
    from ..models import Question, Answer

    logger.info(f"초기 답변 생성 Q: {question_id}")

    question = get_object_or_404(Question, pk=question_id)

    try:
        ai_superuser = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    answer = Answer(
        author=ai_superuser,
        question=question,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    answer.save()

    ai_answer_update_background.schedule(
        1, answer_id=answer.id, question_id=question_id,
        selected_detectors=selected_detectors, selected_predictors=selected_predictors
    )


@background(schedule=1)
def ai_answer_update_background(answer_id, question_id, selected_detectors, selected_predictors):
    """
    백그라운드에서 AI 처리를 실행하고 답변을 업데이트.
    """
    from ..models import Question, Answer
    from .ai import process_image

    logger.info(f"AI 처리 중 Q: {question_id}")

    answer = get_object_or_404(Answer, pk=answer_id)
    question = get_object_or_404(Question, pk=question_id)
    image_path = question.image1.path

    try:
        result_image_path = process_image(image_path, selected_detectors, selected_predictors)
        answer.content = "AI가 처리한 얼굴 인식 결과입니다."
        answer.answer_image = result_image_path
        answer.save()

        logger.info(f"AI 처리 완료 A: {answer.id}")

    except Exception as e:
        logger.exception(f"AI 처리 실패 Q: {question_id}")
        answer.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        answer.modify_date = timezone.now()
        answer.save()
