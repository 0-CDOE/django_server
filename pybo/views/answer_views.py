from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 상태 확인을 위한 믹스인
from django.shortcuts import get_object_or_404, redirect, resolve_url  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티
from django.views.generic import CreateView, UpdateView, DeleteView  # 제네릭 뷰 사용
from django.urls import reverse, reverse_lazy  # URL 처리
from django.contrib.auth.decorators import login_required
import logging  # 로깅을 위한 모듈

# 로깅 설정
logger = logging.getLogger('pybo')

# 필요한 모델과 폼 임포트
from ..models import Question, Answer
from ..forms import AnswerForm


class AnswerFormMixin:
    """
    답변 생성 및 수정 폼 처리를 위한 믹스인 클래스.
    질문 객체를 가져오고, 폼이 유효할 때 데이터를 저장하는 로직을 포함한다.
    """
    
    def get_question(self):
        """
        URL에서 전달된 'pk'를 이용해 질문 객체를 가져온다.
        """
        return get_object_or_404(Question, pk=self.kwargs['pk'])

    def form_valid(self, form):
        """
        폼이 유효할 경우 답변을 저장하고, 해당 질문 상세 페이지로 리다이렉트한다.

        Args:
            form: 제출된 답변 폼.

        Returns:
            redirect: 질문 상세 페이지로 리다이렉트.
        """
        answer = form.save(commit=False)  # 답변 객체 저장, DB 저장은 나중에 수행
        answer.author = self.request.user  # 현재 로그인한 사용자를 답변 작성자로 설정
        answer.create_date = timezone.now()  # 답변 작성 시간을 설정
        answer.question = self.get_question()  # 답변이 달린 질문 객체를 설정
        answer.save()  # 답변을 데이터베이스에 저장

        # 저장된 답변의 질문 상세 페이지로 리다이렉트
        return redirect(reverse('pybo:detail', kwargs={'pk': answer.question.id}))


class AnswerCreateView(LoginRequiredMixin, AnswerFormMixin, CreateView):
    """
    답변 생성 뷰.
    로그인한 사용자만 접근할 수 있으며, AnswerFormMixin을 사용하여 폼 처리를 한다.
    """
    model = Answer
    form_class = AnswerForm
    template_name = 'pybo/base_form.html'


class AnswerUpdateView(LoginRequiredMixin, AnswerFormMixin, UpdateView):
    """
    답변 수정 뷰.
    로그인한 사용자만 접근할 수 있으며, AnswerFormMixin을 사용하여 폼 처리를 한다.
    """
    model = Answer
    form_class = AnswerForm
    template_name = 'pybo/base_form.html'


class AnswerDeleteView(LoginRequiredMixin, DeleteView):
    """
    답변 삭제 뷰.
    로그인한 사용자만 답변을 삭제할 수 있으며, 삭제 후 질문 상세 페이지로 리다이렉트한다.
    """
    model = Answer

    def get(self, request, *args, **kwargs):
        """
        GET 요청 시 삭제 처리.
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
        if request.user != answer.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('pybo:detail', pk=answer.question.pk)

        answer.delete()
        return redirect(reverse_lazy('pybo:detail', kwargs={'pk': answer.question.id}))


@login_required(login_url='common:login')  # 로그인 상태에서만 접근 가능하게 설정
def answer_vote(request, pk):
    """
    답변 추천 기능을 제공하는 뷰.
    로그인한 사용자는 답변을 추천할 수 있으며, 작성자는 자신의 답변을 추천할 수 없다.

    Args:
        request: 추천 요청.
        pk (int): 답변의 ID.

    Returns:
        redirect: 질문 상세 페이지로 리다이렉트 후 해당 답변 위치로 이동.
    """
    answer = get_object_or_404(Answer, pk=pk)  # 답변 객체 가져오기

    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in answer.voter.all():
        messages.error(request, '이미 추천한 답변입니다.')
    else:
        answer.voter.add(request.user)  # 추천 처리

    # 질문 상세 페이지로 리다이렉트 후 해당 답변 위치로 이동
    return redirect('{}#answer_{}'.format(resolve_url('pybo:detail', pk=answer.question.pk), answer.id))


# ===============================================
# AI 관련 백그라운드 처리 함수
# ===============================================
from background_task import background


def create_initial_ai_answer(question_id, selected_detectors, selected_predictors):
    """
    AI 처리 중임을 알리는 초기 답변을 생성하는 함수.
    'AI' 사용자 계정이 답변 작성자로 설정되며, 백그라운드에서 AI 처리를 예약한다.

    Args:
        question_id (int): 질문의 ID
        selected_detectors (list): 선택된 AI 탐지기 목록
        selected_predictors (list): 선택된 AI 예측기 목록
    """
    from django.contrib.auth.models import User
    from ..models import Question, Answer

    logger.info(f"초기 답변 생성 Q: {question_id}")

    # 질문 객체를 가져옴
    question = get_object_or_404(Question, pk=question_id)

    try:
        # AI 슈퍼유저 계정이 존재하는지 확인하고 가져옴
        ai_superuser = User.objects.get(username='AI')
    except User.DoesNotExist:
        logger.error("슈퍼유저 'AI'가 존재하지 않습니다.")
        return

    # AI 유저가 작성한 초기 답변 생성
    answer = Answer(
        author=ai_superuser,
        question=question,
        content="AI가 처리 중입니다.",
        create_date=timezone.now(),
    )
    answer.save()

    # 백그라운드에서 AI 처리를 예약
    ai_answer_update_background(
        answer_id=answer.id,
        question_id=question_id,
        selected_detectors=selected_detectors,
        selected_predictors=selected_predictors,
        schedule=1  # 1초 뒤 실행
    )


@background(schedule=1)
def ai_answer_update_background(answer_id, question_id, selected_detectors, selected_predictors):
    """
    백그라운드에서 AI 처리를 실행하고, 처리 결과를 답변으로 업데이트하는 함수.

    Args:
        answer_id (int): 답변의 ID
        question_id (int): 질문의 ID
        selected_detectors (list): 선택된 AI 탐지기 목록
        selected_predictors (list): 선택된 AI 예측기 목록
    """
    from ..models import Question, Answer
    from .ai import process_image

    logger.info(f"AI 처리 중 Q: {question_id}")

    # 답변과 질문 객체를 가져옴
    answer = get_object_or_404(Answer, pk=answer_id)
    question = get_object_or_404(Question, pk=question_id)
    image_path = question.image1.path

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
