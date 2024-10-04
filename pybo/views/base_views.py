from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from django.db.models import Q

from ..url_patterns import URLS

import logging
logger = logging.getLogger(URLS['APP_NAME'])


class BaseListView(ListView):
    """
    공통 목록 뷰. 모델과 템플릿 이름만 설정해 사용 가능.
    """
    paginate_by = 10  # 한 페이지에 보여줄 항목 수
    template_name = ''  # 사용할 템플릿 지정 (하위 클래스에서 설정 필요)
    search_fields = []  # 검색 필드 (하위 클래스에서 설정 필요)

    def get_queryset(self):
        """ 검색어 필터링 및 최신순 정렬 """
        kw = self.request.GET.get('kw', '')  # 검색어
        logger.info(f"검색어: {kw}")
        object_list = self.model.objects.order_by('-create_date')  # 최신순 정렬

        if kw and self.search_fields:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': kw})
            object_list = object_list.filter(query).distinct()

        return object_list

    def get_context_data(self, **kwargs):
        """ 페이지 및 검색어를 컨텍스트에 추가하고 인덱스를 계산 """
        context = super().get_context_data(**kwargs)
        context['page'] = self.request.GET.get('page', '1')  # 현재 페이지 번호
        context['kw'] = self.request.GET.get('kw', '')  # 검색어

        # 페이지 인덱스 계산
        page_obj = context['paginator'].get_page(context['page'])
        start_index = page_obj.start_index()
        object_indices = [(start_index + i, obj) for i, obj in enumerate(page_obj.object_list)]
        context['object_indices'] = object_indices

        return context


class BaseDetailView(DetailView):
    """
    공통 상세 뷰. 모델과 템플릿 이름만 설정해 사용 가능.
    """
    template_name = ''  # 사용할 템플릿 지정 (하위 클래스에서 설정 필요)
    context_object_name = 'object' # 템플릿에서 사용할 모델 객체 이름

    def get_context_data(self, **kwargs):
        """ 기본 컨텍스트 외에 추가 데이터 처리 가능 """
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        comments = post.comments.all()

        processed_comments = self._set_context_byME(comments)
        # 템플릿에 필요한 데이터를 추가
        context.update({
            'is_object_author': self.request.user == post.author,  # 질문 작성자인지 여부
            'processed_comments': processed_comments,  # 답변 데이터
        })
        return context
    
    def _set_context_byME(self, comments):
        # 각 답변이 현재 사용자의 답변인지 여부 확인 및 추가 데이터 처리
        processed_comments = []
        for comment in comments:
            is_author = self.request.user == comment.author
            is_ai_processing = (comment.content == "AI가 처리 중입니다." and comment.author.username == "AI")
            processed_comments.append({
                'id': comment.id,
                'content': comment.content,
                'is_author': is_author,
                'is_ai_processing': is_ai_processing,
                'image1': comment.image1.url if comment.image1 else None,
                'image2': comment.image2.url if comment.image2 else None,
                'modify_date': comment.modify_date,
                'author_username': comment.author.username,
                'create_date': comment.create_date,
                'voter_count': comment.voter.count(),
            })
            
        return processed_comments


class BaseFormMixin: # 나중에 아래에서 다중상속을 통해 장고 기본 메서드를 오버라이딩할 수 있음
    """
    공통 생성/수정 폼 처리 믹스인. 
    이미지 저장 로직 및 기본 폼 처리를 제공.
    """
    model = NotImplemented
    form_class = None
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial_image1_url'] = (
            self.object.image1.url if self.object and self.object.image1 else None
        )
        context['initial_image2_url'] = (
            self.object.image2.url if self.object and self.object.image2 else None
        )
        return context

    def _save_uploaded_images_byME(self, obj): # CBV의 기본 메서드와의 혼동을 피하기 위한 메서드명
        if 'image1' in self.request.FILES:
            obj.image1 = self.request.FILES['image1']
        if 'image2' in self.request.FILES:
            obj.image2 = self.request.FILES['image2']

    def form_valid(self, form):
        obj = form.save(commit=False)
        if not obj.pk:
            obj.author = self.request.user
            obj.create_date = timezone.now()
        else:
            obj.modify_date = timezone.now()

        self._save_uploaded_images_byME(obj)
        obj.save()
        
        return redirect(reverse_lazy(self.success_url, kwargs={'pk': obj.pk}))


class BaseCreateView(LoginRequiredMixin, BaseFormMixin, CreateView):
    """
    공통 생성 뷰.
    로그인한 사용자만 접근할 수 있으며, 폼을 처리한다.
    """
    pass

class BaseUpdateView(LoginRequiredMixin, BaseFormMixin, UpdateView):
    """
    공통 수정 뷰.
    로그인한 사용자만 접근할 수 있으며, 폼을 처리한다.
    BaseCreateView와 같아보이지만, 
    UpdateView 내부에는 get 메서드와 post 메서드가 있어 기존 답변을 가져오고 수정한다.
    이 점이 BaseCreateView와 다르다.
    """
    pass


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    공통 삭제 뷰.
    로그인한 사용자만 접근할 수 있으며, 삭제 후 메인 페이지로 리다이렉트한다.
    """

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user != obj.author:
            messages.error(request, '삭제 권한이 없습니다.')
            return redirect(reverse(self.success_url, kwargs={'pk': obj.pk}))

        obj.delete()
        return redirect(reverse_lazy(self.success_url))


class BaseVoteView(LoginRequiredMixin, RedirectView):
    """
    공통 추천 뷰.
    사용자는 추천할 수 있으며, 자신의 글은 추천할 수 없다.
    """
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(self.model, pk=kwargs['pk'])

        if self.request.user == obj.author:
            messages.error(self.request, '본인이 작성한 글은 추천할 수 없습니다.')
        elif self.request.user in obj.voter.all():
            messages.error(self.request, '이미 추천하였습니다.')
        else:
            obj.voter.add(self.request.user)
            messages.success(self.request, '추천하였습니다.')

        return reverse(self.success_url, kwargs={'pk': obj.pk})
