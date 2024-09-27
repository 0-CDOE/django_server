from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
import logging  # 로그 출력을 위한 모듈

logger = logging.getLogger('pybo')  # 'pybo'라는 로거 생성

from ..forms import QuestionForm
from ..models import Question


from .answer_views import create_initial_ai_answer

########################################################################################################

@login_required(login_url='common:login')
def question_create(request):
    """ pybo 질문 등록 """
    # POST 요청이면 폼 데이터 처리
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)  # 파일 업로드 처리
        # 폼이 유효한 경우
        if form.is_valid():
            question = form.save(commit=False)  # 데이터베이스에 저장하지 않고, 객체만 반환
            question.author = request.user  # 작성자는 현재 로그인한 사용자
            question.create_date = timezone.now()  # 현재 시간을 질문 작성일로 저장            
            
            # 이미지 파일 저장
            if 'image1' in request.FILES:
                question.image1 = request.FILES['image1']
            if 'image2' in request.FILES:
                question.image2 = request.FILES['image2']
                
            question.save() # 최종적으로 질문을 데이터베이스에 저장
                            # save 후 question 객체에 id 값이 저장됨
            
            selected_detectors = request.POST.getlist('detectors')  # 선택된 탐지기 가져오기
            selected_predictors = request.POST.getlist('predictors')  # 선택된 예측기 가져오기
            
            # 탐지기가 선택된 경우 AI 처리를 백그라운드에서 수행
            if selected_detectors:
                logger.info(f"AI 처리 시작 Q: {question.id}")
                # request 객체 대신 필요한 정보만 전달
                create_initial_ai_answer(
                    question_id=question.id,
                    user_id=request.user.id,
                    selected_detectors=selected_detectors,
                    selected_predictors=selected_predictors
                )
                
            # 성공 시 JsonResponse로 리다이렉트 URL 반환
            return JsonResponse({'redirect_url': reverse('pybo:detail', args=[question.id])})
        else:
            # 폼이 유효하지 않은 경우, 에러 메시지 반환
            return JsonResponse({'error': form.errors}, status=400)
    else:
        # GET 요청일 경우 빈 폼 생성
        form = QuestionForm()
    
    # 템플릿에 폼을 전달하여 렌더링
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

########################################################################################################

@login_required(login_url='common:login')
def question_modify(request, question_id):
    """ pybo 질문 수정 """
    # 수정할 질문을 가져옴, 없으면 404 에러 발생
    question = get_object_or_404(Question, pk=question_id)
    
    # 현재 로그인한 사용자가 작성자가 아닌 경우 에러 메시지 반환
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)

    # POST 요청이면 수정 처리
    if request.method == "POST":
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()  # 수정된 질문 저장
            return JsonResponse({'redirect_url': reverse('pybo:detail', args=[question.id])})
    else:
        # GET 요청이면 기존 데이터를 폼에 담아서 전달
        form = QuestionForm(instance=question)
    
    # 템플릿에 폼을 전달하여 렌더링
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

########################################################################################################

@login_required(login_url='common:login')
def question_delete(request, question_id):
    """ pybo 질문 삭제 """
    # 삭제할 질문을 가져옴, 없으면 404 에러 발생
    question = get_object_or_404(Question, pk=question_id)
    
    # 현재 로그인한 사용자가 작성자가 아닌 경우 에러 메시지 반환
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)

    # 질문 삭제 후 메인 페이지로 리다이렉트
    question.delete()
    return redirect('pybo:index')

########################################################################################################

@login_required(login_url='common:login')
def question_vote(request, question_id):
    """ pybo 질문 추천 """
    # 추천할 질문을 가져옴, 없으면 404 에러 발생
    question = get_object_or_404(Question, pk=question_id)
    
    # 작성자가 본인의 질문을 추천하려고 하면 에러 메시지 반환
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할 수 없습니다')
    else:
        question.voter.add(request.user)  # 추천 처리
    
    # 질문 상세 페이지로 리다이렉트
    return redirect('pybo:detail', question_id=question.id)

########################################################################################################

