from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from common.forms import UserForm
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
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


class CustomLoginView(BaseExtraContextMixin, FormView):
    """
    사용자 로그인 폼을 처리하는 뷰입니다.
    
    사용자가 로그인 폼을 제출하면, 인증 절차를 거쳐 성공 시 메인 페이지로 리다이렉트합니다.

    Attributes
    ----------
    template_name : str
        렌더링할 템플릿 파일의 경로입니다.
    form_class : AuthenticationForm
        사용할 로그인 폼 클래스입니다.
    success_url : str
        로그인 성공 후 리다이렉트할 URL입니다.

    Methods
    -------
    form_valid(form):
        폼이 유효할 경우 로그인 처리를 하고, 성공 시 리다이렉트합니다.
    """
    
    template_name = 'common/login.html'  # 로그인 템플릿 파일
    form_class = AuthenticationForm  # 사용할 폼 클래스 (Django 기본 제공 인증 폼)
    success_url = reverse_lazy('pybo:index')  # 로그인 성공 후 리다이렉트할 URL

    def form_valid(self, form):
        """
        폼이 유효할 경우 실행되는 메서드.
        사용자를 인증하고 로그인 처리 후 성공 페이지로 리다이렉트합니다.

        Parameters
        ----------
        form : AuthenticationForm
            제출된 로그인 폼입니다.

        Returns
        -------
        HttpResponseRedirect
            로그인 성공 후 리다이렉트될 URL로 이동합니다.
        """
        user = form.get_user()  # 폼에서 인증된 사용자 객체를 가져옴
        login(self.request, user)  # 사용자 로그인 처리
        return super().form_valid(form)  # 부모 클래스의 form_valid 메서드를 호출하여 리다이렉트 처리


class SignupView(BaseExtraContextMixin, FormView):
    """
    회원가입 폼을 처리하는 뷰입니다.
    
    사용자가 회원가입 폼을 제출하면, 폼 유효성 검사를 거쳐 새로운 사용자를 생성하고, 로그인 후 성공 페이지로 리다이렉트합니다.

    Attributes
    ----------
    template_name : str
        렌더링할 템플릿 파일의 경로입니다.
    form_class : UserForm
        사용할 회원가입 폼 클래스입니다.
    success_url : str
        회원가입 성공 후 리다이렉트할 URL입니다.

    Methods
    -------
    form_valid(form):
        폼이 유효할 경우 사용자를 생성하고 로그인 처리 후 성공 페이지로 리다이렉트합니다.
    """
    
    template_name = 'common/signup.html'  # 회원가입 템플릿 파일
    form_class = UserForm  # 사용할 회원가입 폼 클래스
    success_url = reverse_lazy('pybo:index')  # 회원가입 성공 후 리다이렉트할 URL

    def form_valid(self, form):
        """
        폼이 유효할 경우 실행되는 메서드.
        새로운 사용자를 생성하고 로그인 처리 후 성공 페이지로 리다이렉트합니다.

        Parameters
        ----------
        form : UserForm
            제출된 회원가입 폼입니다.

        Returns
        -------
        HttpResponseRedirect
            회원가입 성공 후 리다이렉트될 URL로 이동합니다.
        """
        user = form.save()  # 폼을 통해 새로운 사용자 저장
        username = form.cleaned_data.get('username')  # 폼에서 입력한 사용자 이름 가져오기
        raw_password = form.cleaned_data.get('password1')  # 폼에서 입력한 비밀번호 가져오기
        
        # 사용자 인증 처리
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(self.request, user)  # 인증된 사용자 로그인 처리
        return super().form_valid(form)  # 부모 클래스의 form_valid 메서드를 호출하여 리다이렉트 처리


def page_not_found(request, exception):
    """
    404 에러 페이지를 처리하는 함수형 뷰입니다.
    
    존재하지 않는 페이지에 접근할 때 404 에러 페이지를 렌더링합니다.

    Parameters
    ----------
    request : HttpRequest
        클라이언트의 요청 객체입니다.
    exception : Exception
        발생한 예외 객체입니다.

    Returns
    -------
    HttpResponse
        404 에러 페이지를 렌더링한 응답 객체를 반환합니다.
    """
    return render(request, 'common/404.html', {})
