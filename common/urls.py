from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, SignupView

app_name = 'common'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'), # 로그인 처리를 위한 URL 패턴
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'), # 회원가입 처리를 위한 URL 패턴
]
