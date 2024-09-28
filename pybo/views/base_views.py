from django.db.models import Q  # 검색 조건을 위한 Q 객체
from django.views.generic import ListView, DetailView  # 제네릭 뷰 사용
import logging  # 로그 출력을 위한 모듈

logger = logging.getLogger('pybo')  # 'pybo'라는 로거 생성

from ..models import Question  # Question 모델 가져오기
from ..forms import AnswerForm


class QuestionListView(ListView):
    model = Question
    template_name = 'pybo/question_list.html'  # 사용할 템플릿
    paginate_by = 10  # 한 페이지에 보여줄 질문 개수

    def get_queryset(self):
        """ 검색어 필터링 및 최신순 정렬 """
        kw = self.request.GET.get('kw', '')  # 검색어
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
    template_name = 'pybo/question_detail.html'  # 사용할 템플릿
    context_object_name = 'question'  # 템플릿에서 사용할 변수명
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AnswerForm()  # 답변 등록 폼을 컨텍스트에 추가
        return context