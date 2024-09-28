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


class QuestionCreateView(LoginRequiredMixin, CreateView):
    """
    질문 생성 뷰
    사용자가 질문을 작성하고, 선택된 AI 탐지기와 예측기를 처리한 후
    질문을 저장하는 로직을 처리합니다.
    """
    model = Question  # Question 모델을 기반으로 뷰를 생성
    form_class = QuestionForm  # QuestionForm 폼을 사용
    template_name = 'pybo/question_form.html'  # 사용할 템플릿 설정
    login_url = 'common:login'  # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트

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
        질문을 저장하고 AI 탐지기를 백그라운드에서 처리합니다.
        """
        # 질문 객체 생성하되 DB에 저장하지 않음
        question = form.save(commit=False)
        question.author = self.request.user  # 작성자를 현재 로그인 사용자로 설정
        question.create_date = timezone.now()  # 작성 시간을 현재 시간으로 설정

        # 이미지 저장 로직 호출
        self.save_images(question)
        question.save()  # 질문을 DB에 저장

        # 선택된 AI 탐지기 및 예측기 처리
        selected_detectors = self.request.POST.getlist('detectors')  # 탐지기 리스트 가져오기
        selected_predictors = self.request.POST.getlist('predictors')  # 예측기 리스트 가져오기

        # 선택된 AI 탐지기가 있을 경우 AI 처리 시작
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


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    """
    질문 수정 뷰
    질문 작성자가 질문을 수정하고 저장한 후, 질문 상세 페이지로 리다이렉트합니다.
    """
    model = Question  # Question 모델을 기반으로 뷰를 생성
    form_class = QuestionForm  # QuestionForm 폼을 사용
    template_name = 'pybo/question_form.html'  # 사용할 템플릿 설정
    login_url = 'common:login'  # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트

    def form_valid(self, form):
        """
        폼이 유효할 경우 호출됩니다.
        질문을 수정하고 저장한 후, 질문 상세 페이지로 리다이렉트합니다.
        """
        question = form.save(commit=False)  # 질문을 DB에 저장하지 않고 객체 생성
        question.modify_date = timezone.now()  # 수정 시간을 현재 시간으로 설정
        question.save()  # 질문을 DB에 저장

        # AJAX 요청인 경우 JSON 응답, 아니면 리다이렉트 처리
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'redirect_url': reverse('pybo:detail', args=[question.id])})
        else:
            return redirect('pybo:detail', pk=question.id)  # 일반 요청 시 리다이렉트



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
        messages.success(request, '질문이 삭제되었습니다.')
        return redirect(self.success_url)


class QuestionVoteAjaxView(LoginRequiredMixin, View):
    """
    질문 추천 뷰
    사용자가 본인이 작성하지 않은 질문을 추천할 수 있습니다.
    추천은 비동기로 처리되어 페이지를 새로고침하지 않고도 추천할 수 있습니다.
    """
    def post(self, request, *args, **kwargs):
        """
        POST 요청을 통해 질문을 추천합니다.
        작성자는 자신의 질문을 추천할 수 없도록 처리합니다.
        """
        # 질문 객체를 가져옴
        question = get_object_or_404(Question, pk=self.kwargs['pk'])

        # 작성자가 자신의 질문을 추천할 수 없도록 처리
        if request.user == question.author:
            return JsonResponse({'error': '본인이 작성한 글은 추천할 수 없습니다'}, status=400)
        
        # 중복 추천 방지: 이미 추천한 사용자는 추천을 취소함
        if request.user in question.voter.all():
            question.voter.remove(request.user)
            message = '이미 추천 하셨습니다.'
        else:
            question.voter.add(request.user)
            message = '질문을 추천했습니다.'

        # 성공 시 추천 수와 메시지 반환
        return JsonResponse({'voter_count': question.voter.count(), 'message': message})

