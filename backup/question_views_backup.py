from django.contrib import messages  # 사용자에게 메시지를 전달하는 모듈
from django.contrib.auth.mixins import LoginRequiredMixin  # 로그인 상태 확인을 위한 믹스인
from django.shortcuts import get_object_or_404, redirect  # 객체 조회 및 리다이렉트 기능
from django.utils import timezone  # 시간 처리를 위한 유틸리티
from django.urls import reverse_lazy  # URL 처리
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView  # 제네릭 뷰 사용
from django.db.models import Q  # 검색 조건을 위한 Q 객체
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import logging  # 로깅을 위한 모듈
logger = logging.getLogger('pybo')  # pybo 로깅 설정

# 필요한 폼과 모델 임포트
from ..forms import QuestionForm, AnswerForm # Form class 임포트
from ..models import Question  # Question 모델 임포트
from .answer_views_backup import create_initial_ai_answer  # AI 처리 함수 임포트

from ..url_patterns import URLS

question_detail_url = f'{URLS.APP_NAME}:{URLS.QUESTION_DETAIL}'  # 질문 상세 페이지 URL
question_list_url = f'{URLS.APP_NAME}:{URLS.QUESTION_LIST}'  # 질문 목록 페이지 URL



class QuestionListView(ListView):
    model = Question
    template_name = 'pybo/question_list.html'  # 사용할 템플릿
    paginate_by = 10  # 한 페이지에 보여줄 질문 개수

    def get_queryset(self):
        """ 검색어 필터링 및 최신순 정렬 """
        kw = self.request.GET.get('kw', '')  # 검색어
        logger.info(f"검색어: {kw}")  # 검색어를 로그로 출력
        question_list = Question.objects.order_by('-create_date')  # 최신순 정렬

        if kw:
            question_list = question_list.filter(
                Q(subject__icontains=kw) |  # 제목에 검색어 포함
                Q(content__icontains=kw) |  # 내용에 검색어 포함
                Q(answer__content__icontains=kw) |  # 답변 내용에 검색어 포함
                Q(author__username__icontains=kw) |  # 질문 글쓴이 이름에 검색어 포함
                Q(answer__author__username__icontains=kw)  # 답변 글쓴이 이름에 검색어 포함
            ).distinct()  # 중복 제거

        return question_list

    def get_context_data(self, **kwargs):
        """ 페이지 및 검색어를 컨텍스트에 추가하고 질문 인덱스를 계산 """
        context = super().get_context_data(**kwargs)
        # 현재 페이지 번호 및 검색어
        context['page'] = self.request.GET.get('page', '1')  # 현재 페이지 번호
        context['kw'] = self.request.GET.get('kw', '')  # 검색어

        # 질문 인덱스 계산 (현재 페이지의 첫 번째 질문부터 번호 매김)
        page_obj = context['paginator'].get_page(context['page'])  # 현재 페이지의 객체
        start_index = page_obj.start_index()  # 현재 페이지에서 첫 번째 질문의 전체 인덱스
        question_indices = [(start_index + i, question) for i, question in enumerate(page_obj.object_list)]

        # question_indices를 템플릿에 전달
        context['question_indices'] = question_indices
        return context


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'pybo/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        answers = question.answers.all()

        # 각 답변이 현재 사용자의 답변인지 여부 확인 및 추가 데이터 처리
        processed_answers = []
        for answer in answers:
            is_author = self.request.user == answer.author
            is_ai_processing = (answer.content == "AI가 처리 중입니다." and answer.author.username == "AI")
            processed_answers.append({
                'id': answer.id,
                'content': answer.content,
                'is_author': is_author,
                'is_ai_processing': is_ai_processing,
                'answer_image': answer.answer_image.url if answer.answer_image else None,
                'modify_date': answer.modify_date,
                'author_username': answer.author.username,
                'create_date': answer.create_date,
                'voter_count': answer.voter.count(),
            })

        # 템플릿에 필요한 데이터를 추가
        context.update({
            'form': AnswerForm(),
            'is_question_author': self.request.user == question.author,  # 질문 작성자인지 여부
            'processed_answers': processed_answers,  # 답변 데이터
        })
        
        return context

class QuestionFormMixin:
    """
    질문 생성 및 수정 폼 처리를 위한 믹스인 클래스.
    이미지 저장 및 AI 처리 로직을 포함한다.

    Attributes:
        model (Model): Question 모델.
        form_class (Form): QuestionForm을 사용하여 폼을 처리.
        template_name (str): 폼을 렌더링할 템플릿 경로.
    """
    
    model = Question
    form_class = QuestionForm
    template_name = 'pybo/question_form.html'

    def get_context_data(self, **kwargs):
        """
        템플릿에 전달할 추가 컨텍스트 데이터를 생성한다.
        기존 이미지 URL을 템플릿에 전달하여 수정 시 미리보기를 가능하게 한다.

        Args:
            **kwargs: 추가 컨텍스트 인자.

        Returns:
            dict: 템플릿에 전달할 컨텍스트 데이터.
        """
        context = super().get_context_data(**kwargs)
        context['initial_image1_url'] = (
            self.object.image1.url if self.object and self.object.image1 else None
        )
        context['initial_image2_url'] = (
            self.object.image2.url if self.object and self.object.image2 else None
        )
        return context

    def save_uploaded_images(self, question):
        """
        업로드된 이미지를 질문 객체에 저장한다.
        request.FILES에서 파일을 가져와 질문 객체에 이미지1, 이미지2를 저장한다.

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
        질문을 저장하고 AI 탐지기를 백그라운드에서 처리한다.

        Args:
            form: 제출된 질문 폼.

        Returns:
            redirect: 질문 상세 페이지로 리다이렉트.
        """
        # 질문 객체 생성 (commit=False로 DB에 저장하지 않고 객체만 반환)
        question = form.save(commit=False)

        # 작성자 및 생성/수정 날짜 설정
        if not question.pk:  # 새 질문 생성
            question.author = self.request.user
            question.create_date = timezone.now()
        else:  # 기존 질문 수정
            question.modify_date = timezone.now()

        # 업로드된 이미지 저장
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
        return redirect(reverse(question_detail_url, kwargs={'pk': question.id}))


class QuestionCreateView(LoginRequiredMixin, QuestionFormMixin, CreateView):
    """
    질문 생성 뷰.
    로그인한 사용자만 접근할 수 있으며, 질문 생성 폼을 처리한다.
    """
    pass


class QuestionUpdateView(LoginRequiredMixin, QuestionFormMixin, UpdateView):
    """
    질문 수정 뷰.
    로그인한 사용자만 접근할 수 있으며, 질문 수정 폼을 처리한다.
    """
    pass


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    """
    질문 삭제 뷰.
    로그인한 사용자만 질문을 삭제할 수 있으며, 삭제 후 메인 페이지로 리다이렉트한다.
    """
    
    model = Question

    def get(self, request, *args, **kwargs):
        """
        GET 요청 시 바로 삭제를 처리한다.

        Args:
            request: HTTP 요청 객체.

        Returns:
            redirect: 삭제 후 메인 페이지로 리다이렉트.
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
        
        # 삭제 권한이 없으면 에러 메시지 출력 후 질문 상세 페이지로 리다이렉트
        if request.user != question.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect(question_detail_url, pk=question.pk)

        question.delete()
        # 메인 페이지로 리다이렉트
        return redirect(reverse_lazy(question_list_url))


@login_required(login_url='common:login')
def vote_question(request, pk):
    """
    질문 추천 기능을 제공하는 뷰.
    사용자는 질문을 추천할 수 있으며, 자신이 작성한 질문은 추천할 수 없다.

    Args:
        request: 사용자의 요청.
        pk (int): 질문의 ID.

    Returns:
        redirect: 질문 상세 페이지로 리다이렉트.
    """
        
    # 추천할 질문을 가져오고, 없으면 404 에러 발생
    question = get_object_or_404(Question, pk=pk)

    # 본인의 질문을 추천하려고 하면 에러 메시지 출력
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다.')
    elif request.user in question.voter.all():
        messages.error(request, '이미 추천한 질문입니다.')
    else:
        question.voter.add(request.user)  # 추천 처리

    # 질문 상세 페이지로 리다이렉트
    
    return redirect(question_detail_url, pk=question.id)


class QuestionVoteView(LoginRequiredMixin, RedirectView):
    """
    질문 추천 기능을 처리하는 제네릭 뷰.
    로그인한 사용자는 질문을 추천할 수 있으며, 본인의 질문은 추천할 수 없다.
    """
    
    permanent = False  # 임시 리다이렉트
    query_string = True  # URL에 추가적인 쿼리 스트링 전달 가능

    def get_redirect_url(self, *args, **kwargs):
        """
        추천 처리 후, 질문 상세 페이지로 리다이렉트한다.
        
        Args:
            *args: 추가적인 인자.
            **kwargs: URL 패턴에 필요한 매개변수 (예: 질문 ID).
        
        Returns:
            str: 리다이렉트할 URL.
        """
        question = get_object_or_404(Question, pk=kwargs['pk'])

        if self.request.user == question.author:
            messages.error(self.request, '본인이 작성한 글은 추천할 수 없습니다.')
        elif self.request.user in question.voter.all():
            messages.error(self.request, '이미 추천한 질문입니다.')
        else:
            question.voter.add(self.request.user)
            messages.success(self.request, '질문을 추천했습니다.')
        
        # 리다이렉트할 URL 반환 (질문 상세 페이지)
        return reverse(question_detail_url, kwargs={'pk': question.pk})

