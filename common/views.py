from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from common.forms import UserForm

def index(request):
    return render(request, 'common/index.html')  

def logout_view(request):
    logout(request)
    return redirect('common:index')

def signup(request):
    """
    회원가입 처리
    """
    if request.method == "POST": # POST 요청일 때
        form = UserForm(request.POST)
        if form.is_valid(): # 폼 검증에 성공하면
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect('common:index')
    else: # GET 요청일 때
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

def page_not_found(request, exception):
    return render(request, 'common/404.html', {})