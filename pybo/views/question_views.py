from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 상태 확인을 위한 믹스인
from django.shortcuts import get_object_or_404, redirect  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티
from django.http import JsonResponse  # JSON 응답 처리
from django.urls import reverse, reverse_lazy  # URL 처리
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView  # 제네릭 뷰 사용
import logging  # 로깅을 위한 모듈

# 로깅 설정
logger = logging.getLogger('pybo')

# 필요한 폼과 모델 임포트
from ..forms import QuestionForm  # QuestionForm 임포트
from ..models import Question  # Question 모델 임포트
from .answer_views import create_initial_ai_answer  # AI 처리 함수 임포트


class QuestionFormMixin:
    """
    Question 생성 및 수정을 위한 공통 로직 Mixin.
    """
    def save_images(self, question):
        """
        이미지 저장 로직
        업로드된 이미지 파일들을 질문 객체에 저장합니다.
        """
        if 'image1' in self.request.FILES:
            question.image1 = self.request.FILES['image1']  # 이미지1 저장
        if 'image2' in self.request.FILES:
            question.image2 = self.request.FILES['image2']  # 이미지2 저장

    def form_valid(self, form):
        """
        폼이 유효할 경우 호출됩니다.
        질문을 저장하고 선택된 AI 탐지기를 백그라운드에서 처리합니다.
        """
        # 질문 객체 생성, DB에 저장하지 않고 객체만 반환
        question = form.save(commit=False)
        if not question.id:
            # 새로 생성하는 경우에는 작성자와 작성 시간을 설정
            question.author = self.request.user
            question.create_date = timezone.now()
        else:
            # 수정하는 경우에는 수정 시간을 설정
            question.modify_date = timezone.now()

        # 이미지 저장 로직 호출
        self.save_images(question)
        question.save()  # 질문을 DB에 저장

        # 선택된 AI 탐지기 및 예측기 처리 (생성일 경우에만 처리)
        if not question.modify_date:
            selected_detectors = self.request.POST.getlist('detectors')  # 탐지기 리스트 가져오기
            selected_predictors = self.request.POST.getlist('predictors')  # 예측기 리스트 가져오기

            if selected_detectors:
                logger.info(f"AI 처리 시작 Q: {question.id}")
                try:
                    # 백그라운드 작업으로 AI 처리 함수 호출
                    create_initial_ai_answer(
                        question_id=question.id,
                        user_id=self.request.user.id,
                        selected_detectors=selected_detectors,
                        selected_predictors=selected_predictors
                    )
                    logger.info(f"AI 처리 완료 Q: {question.id}")
                except Exception as e:
                    logger.error(f"AI 처리 실패 Q: {question.id}, Error: {str(e)}")

        # AJAX 요청인 경우 JSON 응답, 일반 요청인 경우 리다이렉트 처리
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': reverse('pybo:detail', args=[question.id])})
        else:
            return redirect('pybo:detail', pk=question.id)  # 일반 요청 시 리다이렉트

class QuestionCreateView(LoginRequiredMixin, QuestionFormMixin, CreateView):
    """
    질문 생성 뷰
    """
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'
    login_url = 'common:login'


class QuestionUpdateView(LoginRequiredMixin, QuestionFormMixin, UpdateView):
    """
    질문 수정 뷰
    """
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'
    login_url = 'common:login'




class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    model = Question
    success_url = reverse_lazy('pybo:index')  # 삭제 후 리다이렉트할 URL

    def get(self, request, *args, **kwargs):
        """
        GET 요청을 받으면 바로 삭제 처리.
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        POST 요청으로 질문을 삭제한 후, 질문 목록 페이지로 리다이렉트.
        """
        question = self.get_object()
        if request.user != question.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect('pybo:detail', pk=question.pk)

        question.delete()
        return redirect(self.success_url)

from django.contrib.auth.decorators import login_required

@login_required
def question_vote_ajax(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.user == question.author:
        messages.error(request, '자신의 질문은 추천할 수 없습니다.')
        return JsonResponse({'voter_count': question.voter.count(), 'message': '자신의 질문은 추천할 수 없습니다.', 'status': 'error'}, status=400)

    if request.user in question.voter.all():
        question.voter.remove(request.user)  # 추천 취소
        messages.success(request, '추천을 취소했습니다.')
        message_text = '추천을 취소했습니다.'
    else:
        question.voter.add(request.user)  # 추천 추가
        messages.success(request, '추천했습니다.')
        message_text = '추천했습니다.'

    return JsonResponse({
        'voter_count': question.voter.count(),
        'message': message_text,
        'status': 'success'
    })
