from django.urls import path
from .views import base_views, question_views, answer_views

app_name = 'pybo'  # URL 네임스페이스. 다른 앱의 URL 패턴과 충돌하지 않도록 설정

urlpatterns = [
    path('', base_views.QuestionListView.as_view(), name='index'),
    path('<int:pk>/', base_views.QuestionDetailView.as_view(), name='detail'),
    
    path('question/create/', question_views.QuestionCreateView.as_view(), name='question_create'),
    path('question/update/<int:pk>/', question_views.QuestionUpdateView.as_view(), name='question_update'),
    path('question/delete/<int:pk>/', question_views.QuestionDeleteView.as_view(), name='question_delete'),
    path('question/vote/ajax/<int:pk>/', question_views.question_vote_ajax, name='question_vote'),
    
    path('answer/create/<int:pk>/', answer_views.AnswerCreateView.as_view(), name='answer_create'),
    path('answer/update/<int:pk>/', answer_views.AnswerUpdateView.as_view(), name='answer_update'),
    path('answer/delete/<int:pk>/', answer_views.AnswerDeleteView.as_view(), name='answer_delete'),
    path('answer/vote/<int:pk>/', answer_views.answer_vote, name='answer_vote'),
]
