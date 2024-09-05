from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
import logging
logger = logging.getLogger('pybo')

from ..models import Question

def index(request):
    ''' pybo 목록 출력 '''
    logger.info("INFO 레벨로 출력")
    #
    # 입력인자
    # 페이지 번호를 GET 요청에서 받아옵니다. 기본값은 1로 설정되어 있습니다.
    page = request.GET.get('page', '1')  # GET 방식으로 'page' 값을 받아 page 변수에 할당, 값이 없으면 1을 기본값으로 사용
    #
    # 검색어를 GET 요청에서 받아옵니다. 기본값은 빈 문자열입니다.
    kw = request.GET.get('kw', '')  # 검색어
    #
    # 조회
    # Question 모델에서 모든 질문을 가져와 작성일시(create_date) 역순으로 정렬합니다.
    question_list = Question.objects.order_by('-create_date')  # Question 모델 데이터를 시간 역순으로 정렬
    #
    # 검색어(kw)가 존재할 경우, 제목, 내용, 답변 내용, 질문 글쓴이, 답변 글쓴이에서 검색어를 포함하는 데이터를 필터링합니다.
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목에 검색어 포함된 경우 필터링
            Q(content__icontains=kw) |  # 내용에 검색어 포함된 경우 필터링
            Q(answer__content__icontains=kw) |  # 답변 내용에 검색어 포함된 경우 필터링
            Q(author__username__icontains=kw) |  # 질문 글쓴이 이름에 검색어 포함된 경우 필터링
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이 이름에 검색어 포함된 경우 필터링
        ).distinct()  # distinct() 메서드를 사용하여 중복된 질문을 제거합니다.
        #
    #
    # 페이징 처리
    # Paginator 클래스를 사용하여 한 페이지에 10개의 질문을 보여줍니다.
    paginator = Paginator(question_list, 10)  # Paginator 객체 생성 (페이지당 10개 항목)
    #
    # page 번호에 해당하는 페이지의 질문들을 가져옵니다.
    page_obj = paginator.get_page(page)  # 현재 페이지에 해당하는 데이터(page_obj)를 가져옴
    #
    # 템플릿에 전달할 context 딕셔너리를 생성합니다.
    # 'Q_list' 키에 page_obj, 'page' 키에 현재 페이지 번호, 'kw' 키에 검색어를 담습니다.


    context = {'QList': page_obj, 'page': page, 'kw': kw}  # 템플릿에 전달할 데이터
    #
    # pybo/question_list.html 템플릿을 렌더링하고 context 데이터를 전달합니다.
    return render(request, 'pybo/question_list.html', context)  # 렌더링하여 사용자에게 응답
    #
#
def detail(request, question_id):
    ''' pybo 내용 출력 '''
    #
    # 주어진 question_id에 해당하는 Question 객체를 가져옵니다.
    # 객체가 없으면 404 오류를 발생시킵니다.
    question = get_object_or_404(Question, pk=question_id)  # pk로 Question 객체를 가져옴, 없으면 404 오류 발생
    #
    # 템플릿에 전달할 context 딕셔너리를 생성합니다.
    #질문에 있는 댓글을 넘겨줌
    comments = question.comments.filter(parent__isnull=True)
    context = {'question': question, 'comments': comments}  # 템플릿에 전달할 데이터


    # pybo/question_detail.html 템플릿을 렌더링하고 context 데이터를 전달합니다.
    return render(request, 'pybo/question_detail.html', context)  # 렌더링하여 사용자에게 응답
    #
#
##################################### 제네릭 뷰 방식 #####################################

# # views.py 파일을 수정하여 클래스 기반 뷰로 변경
# class IndexView(generic.ListView): # ListView 클래스를 상속받아 IndexView 클래스를 정의
#     # IndexView 클래스는 템플릿명이 명시적으로 지정되지 않으면 자동으로 모델명_list.html 템플릿을 찾음
#     """
#     pybo 목록 출력
#     """
#     def get_queryset(self): # get_queryset 메서드를 오버라이딩하여 최신 순으로 정렬된 Question 모델 데이터를 반환
#         return Question.objects.order_by('-create_date')
    
# class DetailView(generic.DetailView):
#     """
#     pybo 내용 출력
#     """
#     model = Question # model 속성에 Question 모델을 지정
########################################################################################################