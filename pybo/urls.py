from django.urls import path

from .views import base_views, question_views, answer_views , comment_view

app_name = 'pybo' # namespace를 사용하면 다른 앱의 URL 패턴과 이름이 중복되더라도 문제가 발생하지 않는다.

"""
path 함수의 첫 번째 인수 : URL 패턴

path 함수의 두 번째 인수 : URL 패턴에 매핑되는 뷰 함수

path 함수의 세 번째 인수 : URL 패턴의 별칭

URL 패턴이 비어있는 경우에는 웹 사이트의 기본 URL이다.

웹 사이트의 기본 URL은 웹 사이트에 접속했을 때 가장 먼저 보여지는 페이지이다.

웹 사이트의 기본 URL은 index 함수를 호출한다.

index 함수는 질문 목록을 보여주는 기능을 한다.

"""

urlpatterns = [
    
    # base_views.py 

    # index 함수 호출
    path('', base_views.index, name='index'),
    # question_id를 매개변수로 받아 detail 함수 호출
    path('<int:question_id>/', base_views.detail, name='detail'),

    # question_views.py

    # question_create 함수 호출
    path('question/create/', question_views.question_create, name='question_create'),
    # question_id를 매개변수로 받아 question_modify 함수 호출
    path('question/modify/<int:question_id>/', question_views.question_modify, name='question_modify'),
    # question_id를 매개변수로 받아 question_delete 함수 호출
    path('question/delete/<int:question_id>/', question_views.question_delete, name='question_delete'),
    # question_id를 매개변수로 받아 question_vote 함수 호출
    path('question/vote/<int:question_id>/', question_views.question_vote, name='question_vote'),

    # answer_views.py 

    # question_id를 매개변수로 받아 answer_create 함수 호출
    path('answer/create/<int:question_id>/', answer_views.answer_create, name='answer_create'),
    # answer_id를 매개변수로 받아 answer_modify 함수 호출
    path('answer/modify/<int:answer_id>/', answer_views.answer_modify, name='answer_modify'),
    # answer_id를 매개변수로 받아 answer_delete 함수 호출
    path('answer/delete/<int:answer_id>/', answer_views.answer_delete, name='answer_delete'),
    # answer_id를 매개변수로 받아 answer_vote 함수 호출
    path('answer/vote/<int:answer_id>/', answer_views.answer_vote, name='answer_vote'),


    path('comment/create/question/<int:question_id>/', comment_view.comment_create_question ,name ='comment_create_question'),
    path('comment/modify/question/<int:comment_id>/', comment_view.comment_modify_question ,name ='comment_modify_question'),
    path('comment/delete/question/<int:comment_id>/', comment_view.comment_delete_question ,name ='comment_delete_question'),




]

###############################################################################################################

# urlpatterns = [
#     # index 함수 호출
#     path('', views.index, name='index'), 
    
#     # question_id를 매개변수로 받아 detail 함수 호출
#     path('<int:question_id>/', views.detail, name='detail'), 
    
#     # question_id를 매개변수로 받아 answer_create 함수 호출
#     path('answer/create/<int:question_id>/', views.answer_create, name='answer_create'), 
    
#     # question_create 함수 호출
#     path('question/create/', views.question_create, name='question_create'), 
    
#     # question_id를 매개변수로 받아 question_modify 함수 호출
#     path('question/modify/<int:question_id>/', views.question_modify, name='question_modify'), 
    
#     # question_id를 매개변수로 받아 question_delete 함수 호출
#     path('question/delete/<int:question_id>/', views.question_delete, name='question_delete'), 
    
#     # answer_id를 매개변수로 받아 answer_modify 함수 호출
#     path('answer/modify/<int:answer_id>/', views.answer_modify, name='answer_modify'),
    
#     # answer_id를 매개변수로 받아 answer_delete 함수 호출
#     path('answer/delete/<int:answer_id>/', views.answer_delete, name='answer_delete'),
# ]

##################################### 제네릭 뷰 방식 #####################################

# urlpatterns = [
#     path('', views.IndexView.as_view()), # IndexView 클래스를 뷰로 사용
#     path('<int:pk>/', views.DetailView.as_view()), # DetailView 클래스를 뷰로 사용
# ]