from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from common.forms import UserForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from common.forms import UserForm
from django.contrib.auth.forms import AuthenticationForm
from pybo.views.base_views import BaseExtraContextMixin
from django.views.generic import TemplateView


class IndexView(BaseExtraContextMixin, TemplateView):
    """
    IndexView는 기본 인덱스 페이지를 처리하는 뷰입니다.

    사용자가 처음으로 접근하는 페이지를 렌더링합니다.

    Attributes
    ----------
    template_name : str
        렌더링할 템플릿 파일의 경로입니다.
    """
    template_name = 'pybo/index.html'  # 사용할 템플릿 파일 지정



# CustomLoginView를 FormView로 수정하여 POST 요청 처리
class CustomLoginView(BaseExtraContextMixin, FormView):
    template_name = 'common/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('pybo:index')  # 로그인 성공 후 리다이렉트할 URL

    def form_valid(self, form):
        """
        폼이 유효할 경우 로그인 처리를 한다.
        """
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
    
# SignupView를 CBV로 변환
class SignupView(BaseExtraContextMixin, FormView):
    """
    회원가입 폼을 처리하는 뷰.
    FormView를 상속받아 폼 제출 및 유효성 검사를 처리하고, 성공 시 리다이렉트한다.
    """
    template_name = 'common/signup.html'  # 회원가입 템플릿 파일
    form_class = UserForm  # 사용할 폼 클래스
    success_url = reverse_lazy('pybo:index')  # 회원가입 성공 후 리다이렉트할 URL

    def form_valid(self, form):
        """
        폼이 유효할 경우 실행되는 메서드.
        사용자를 저장하고, 로그인 처리 후 성공 페이지로 리다이렉트한다.
        """
        # 사용자 저장
        user = form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        # 사용자 인증 및 로그인 처리
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

# page_not_found를 CBV로 변환
def page_not_found(request, exception):
    return render(request, 'common/404.html', {})