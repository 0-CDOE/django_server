from django.urls import path
from django.contrib.auth import views as auth_views
from common import views

app_name = 'common' # namespace를 사용하면 다른 앱의 URL 패턴과 이름이 중복되더라도 문제가 발생하지 않는다.

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'), # 로그인 처리를 위한 URL 패턴
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='index'),
]
