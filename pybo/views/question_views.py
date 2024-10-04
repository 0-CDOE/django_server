from django.urls import reverse


from .base_views import BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView
from ..models import SimilarityPost
from ..forms import QuestionForm, AnswerForm
from .answer_views import create_initial_ai_answer

from ..url_patterns import URLS

# 기본 URL 설정
app_name = URLS['APP_NAME']
board_name = URLS['BOARD_NAME']['similarity']
content_type = URLS['CONTENT_TYPE']
end_point = URLS['CRUD_AND_MORE']

read_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["read"]}'
list_url = f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}'


import logging  # 로깅을 위한 모듈
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 생성
"""
base_views.py에 정의된 BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView를 상속받아
질문 게시판의 뷰를 정의한다.

이 때 템플릿에서 사용할 모델 객체 이름은 'object'로 사용한다.

1.  이 때 템플릿 상에서 해당 모델에 정의된 모든 필드에 접근할 수 있다. (ex. object.author.username)

2.  이 때 템플릿 상에서 해당 모델에 정의된 메서드들도 사용할 수 있다. (ex. object.get_absolute_url())

3.  이 때 템플릿 상에서 해당 모델이 다른 모델과 ForeignKey, ManyToMany, OneToOne 등으로 연결되어 있을 경우,

    related_name으로 관계된 모델 객체에도 접근할 수 있다. (ex. object.comments.all())
                                                                            ..^^^ 연결된 모델에 정의된 메서드
                                                                    ..^^^^^^^ related_name으로 정의된 이름
                                                                    
4.  이 때 템플릿 상에서 Django 모델의 메타 정보를 사용할 수도 있다. (ex. object._meta.verbose_name)
"""
extra_context = {
    'app_name': app_name,
    'board_name': board_name,
}
    
class QuestionListView(BaseListView):
    model = SimilarityPost
    template_name = 'pybo/question_list.html'
    search_fields = ['subject', 'content', 'author__username', 'answer__content', 'answer__author__username']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(extra_context)
        return context

class QuestionDetailView(BaseDetailView):
    model = SimilarityPost
    template_name = 'pybo/question_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = post.comments.all()

        processed_comments = self._set_context_byME(comments)
        # 템플릿에 필요한 데이터를 추가
        context.update({
            'form': AnswerForm(),
            'is_object_author': self.request.user == post.author,  # 질문 작성자인지 여부
            'processed_comments': processed_comments,  # 답변 데이터
        })
        context.update(extra_context)

        
        return context
    
class QuestionCreateView(BaseCreateView):
    model = SimilarityPost
    form_class = QuestionForm
    success_url = read_url
    
    def form_valid(self, form):
        # 상위 클래스의 form_valid 호출 (기존 동작 유지) <<< 오버라이딩은 덮어쓰기의 개념 // 이건 이어쓰기의 개념
        response = super().form_valid(form)
        
        # 추가 작업을 여기에 정의
        
        # 이어쓰기에 필요한 데이터
        obj = form.instance # 질문 객체 부모 부모 클래스의 form_valid에서 생성된 객체 (form.save(commit=False)로 생성된 객체)
        
        # 선택된 AI 탐지기 및 예측기 처리
        selected_detectors = self.request.POST.getlist('detectors')
        selected_predictors = self.request.POST.getlist('predictors')

        if selected_detectors:
            logger.info(f"AI 처리 시작 - 질문: {obj}")
            try:
                create_initial_ai_answer(
                    post_id=obj.id,
                    selected_detectors=selected_detectors,
                    selected_predictors=selected_predictors
                )
                logger.info(f"AI 처리 완료 - 질문 ID: {obj}")
            except Exception as e:
                logger.error(f"AI 처리 실패 - 질문 ID: {obj}, 에러: {str(e)}")
        
        # 상위 클래스의 결과를 반환
        return response
    
class QuestionUpdateView(BaseUpdateView):
    """
    AI 처리 로직을 Base클래스나 Mixin 클래스에서 구현 하지 않고, 
    QuestionCreateView에서 처리함으로써,
    QuestionUpdateView에서는 AI 처리 로직은 구현되지 않도록 함.
    """
    model = SimilarityPost
    form_class = QuestionForm
    success_url = read_url


class QuestionDeleteView(BaseDeleteView):
    model = SimilarityPost
    success_url = list_url


class QuestionVoteView(BaseVoteView):
    model = SimilarityPost
    success_url = read_url
