from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 상태 확인을 위한 믹스인
from django.shortcuts import get_object_or_404, redirect  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티
from django.urls import reverse_lazy  # URL 처리
from django.views.generic import CreateView, UpdateView, DeleteView  # 제네릭 뷰 사용
from django.contrib.auth.decorators import login_required

import logging  # 로깅을 위한 모듈
logger = logging.getLogger('pybo')

# 필요한 폼과 모델 임포트
from ..forms import QuestionForm  # QuestionForm 임포트
from ..models import Question  # Question 모델 임포트
from .answer_views import create_initial_ai_answer  # AI 처리 함수 임포트


class QuestionFormMixin:
    """
    질문 생성 및 수정 폼 처리를 위한 믹스인 클래스.
    이미지 저장 로직과 폼이 유효할 때 호출되는 처리 로직을 포함한다.
    """

    def save_uploaded_images(self, question):
        """
        업로드된 이미지를 질문 객체에 저장하는 함수.
        request.FILES에서 이미지 파일을 가져와 질문 객체에 추가한다.

        Args:
            question (Question): 저장할 질문 객체.
        """
        if 'image1' in self.request.FILES:
            question.image1 = self.request.FILES['image1']
        if 'image2' in self.request.FILES:
            question.image2 = self.request.FILES['image2']

    def form_valid(self, form):
        """
        폼이 유효할 경우 호출되는 메서드.
        질문을 저장하고, AI 탐지기를 백그라운드에서 처리한다.

        Args:
            form: 제출된 질문 폼.

        Returns:
            redirect: 질문 상세 페이지로 리다이렉트.
        """
        # 질문 객체 생성, DB에 저장하지 않고 객체만 반환
        question = form.save(commit=False)

        # 작성자와 작성 날짜 또는 수정 날짜 설정
        if not question.id:
            question.author = self.request.user
            question.create_date = timezone.now()
        else:
            question.modify_date = timezone.now()

        # 이미지 저장 로직 호출
        self.save_uploaded_images(question)
        question.save()  # 질문을 DB에 저장

        # 선택된 AI 탐지기 및 예측기 처리
        selected_detectors = self.request.POST.getlist('detectors')
        selected_predictors = self.request.POST.getlist('predictors')

        if selected_detectors:
            logger.info(f"AI 처리 시작 - 질문 ID: {question.id}")
            try:
                create_initial_ai_answer(
                    question_id=question.id,
                    selected_detectors=selected_detectors,
                    selected_predictors=selected_predictors
                )
                logger.info(f"AI 처리 완료 - 질문 ID: {question.id}")
            except Exception as e:
                logger.error(f"AI 처리 실패 - 질문 ID: {question.id}, 에러: {str(e)}")

        # 질문 상세 페이지로 리다이렉트
        return redirect('pybo:detail', pk=question.id)


class QuestionCreateView(LoginRequiredMixin, QuestionFormMixin, CreateView):
    """
    질문 생성 뷰.
    로그인한 사용자만 접근할 수 있으며, 질문 생성 폼을 처리한다.
    """
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'
    login_url = 'common:login'


class QuestionUpdateView(LoginRequiredMixin, QuestionFormMixin, UpdateView):
    """
    질문 수정 뷰.
    로그인한 사용자만 접근할 수 있으며, 질문 수정 폼을 처리한다.
    """
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'
    login_url = 'common:login'


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    """
    질문 삭제 뷰.
    로그인한 사용자만 질문을 삭제할 수 있으며, 삭제 후 메인 페이지로 리다이렉트한다.
    """
    model = Question

    def get(self, request, *args, **kwargs):
        """
        GET 요청이 들어오면 바로 삭제 처리한다.
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        질문 삭제 처리.
        사용자가 작성한 질문인지 확인 후 삭제하고, 메인 페이지로 리다이렉트한다.

        Args:
            request: 사용자의 요청.

        Returns:
            redirect: 삭제 후 메인 페이지로 리다이렉트.
        """
        question = self.get_object()
        if request.user != question.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('pybo:detail', pk=question.pk)

        question.delete()
        return redirect(reverse_lazy('pybo:index'))


@login_required(login_url='common:login')
def question_vote(request, pk):
    """
    질문 추천 기능을 제공하는 뷰.
    사용자는 질문을 추천할 수 있으며, 자신이 작성한 질문은 추천할 수 없다.

    Args:
        request: 사용자의 요청.
        pk (int): 질문의 ID.

    Returns:
        redirect: 질문 상세 페이지로 리다이렉트.
    """
    # 추천할 질문을 가져옴, 없으면 404 에러 발생
    question = get_object_or_404(Question, pk=pk)

    # 작성자가 본인의 질문을 추천하려고 하면 에러 메시지 반환
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in question.voter.all():
        messages.error(request, '이미 추천한 질문입니다.')
    else:
        question.voter.add(request.user)  # 추천 처리

    # 질문 상세 페이지로 리다이렉트
    return redirect('pybo:detail', pk=question.id)
