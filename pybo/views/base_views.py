from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView, TemplateView
from django.db.models import Q

from ..url_patterns import URLS

import logging
logger = logging.getLogger(URLS['APP_NAME'])  # 로거 설정

# URL 설정
app_name = URLS['APP_NAME']  # 애플리케이션 이름
content_type = URLS['CONTENT_TYPE']  # 컨텐츠 타입
end_point = URLS['CRUD_AND_MORE']  # CRUD 엔드포인트 정보
board_names = URLS['BOARD_NAME'].keys()  # 게시판 이름

# 사용자에게 표시할 게시판 이름
board_name_for_user = {
    'similarity': '얼굴 유사도 비교',
    'detection': '대통령을 찾아라!',
}

# 사용자에게 표시할 게시판 이름 리스트
board_names_for_user = [board_name_for_user[board_name] for board_name in board_names]

# 게시판별 URL 리스트
board_urls = [f'{app_name}:{board_name}_{content_type["post"]}_{end_point["list"]}' for board_name in board_names]


class BaseExtraContextMixin:
    """
    BaseExtraContextMixin 클래스는 각 뷰에서 추가적인 데이터를 템플릿에 전달하기 위한 공통 믹스인입니다.

    이 믹스인을 상속받으면 템플릿에 필요한 추가 데이터를 쉽게 설정할 수 있습니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 추가 데이터를 전달하는 메서드. 게시판 이름, URL 등을 설정합니다.

    Parameters
    ----------
    kwargs : dict
        템플릿에 전달할 추가적인 키워드 인자들(템플릿에서 변수로 사용할 수 있는 모든 데이터)입니다.

    Returns
    -------
    dict
        추가 데이터를 포함한 템플릿 컨텍스트 딕셔너리입니다.
    """
    
    def get_context_data(self, **kwargs) -> dict:
        """
        템플릿에 전달할 추가 데이터를 설정하는 메서드입니다.

        예를 들어, 애플리케이션 이름, 게시판 이름 및 URL, 사용자에게 표시할 게시판 이름을 템플릿에 넘깁니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자(템플릿에서 변수로 사용할 수 있는 모든 데이터)입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        # 부모 클래스의 get_context_data를 호출하여 기본 데이터를 가져옵니다.
        context = super().get_context_data(**kwargs)
        
        # 추가적인 데이터를 템플릿 컨텍스트에 설정합니다.
        context['app_name'] = app_name  # 애플리케이션 이름 설정
        context['board_names'] = board_names  # 게시판 이름 설정
        context['board_urls'] = board_urls  # 게시판 URL 설정
        context['board_names_for_user'] = board_names_for_user  # 사용자용 게시판 이름 설정
        
        return context  # 추가 데이터를 포함한 컨텍스트 반환


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


class BaseListView(ListView):
    """
    BaseListView는 게시글 목록을 표시하는 공통 뷰입니다.

    페이지네이션 및 검색 기능을 포함하고 있으며, 하위 클래스에서 모델과 템플릿을 설정해야 합니다.

    Attributes
    ----------
    paginate_by : int
        한 페이지에 보여줄 게시글 수를 지정합니다.
        
    template_name : str
        사용할 템플릿 파일의 이름을 지정합니다. 하위 클래스에서 설정이 필요합니다.
        
    search_fields : list
        검색할 필드를 지정합니다. 하위 클래스에서 설정이 필요합니다.

    Methods
    -------
    get_queryset():
        게시글 목록을 검색어에 따라 필터링하고 최신순으로 정렬합니다.
    
    get_context_data(**kwargs):
        템플릿에 추가적인 데이터를 전달합니다. 예를 들어, 페이지 번호와 검색어를 설정합니다.
    """
    paginate_by = 10  # 한 페이지에 보여줄 게시글 수
    template_name = ''  # 사용할 템플릿 (하위 클래스에서 설정 필요)
    search_fields = []  # 검색 필드 (하위 클래스에서 설정 필요)

    def get_queryset(self):
        """
        get_queryset 메서드는 게시글 목록을 필터링하고 정렬하여 반환합니다.

        검색어는 'kw'라는 쿼리 파라미터로 전달받으며, 이 검색어를 기준으로 필터링합니다.

        Parameters
        ----------
        None
        
        Returns
        -------
        QuerySet
            필터링되고 정렬된 게시글 QuerySet입니다.
        """
        # 검색어 가져오기 ('kw'라는 GET 파라미터로 전달받음)
        search_keyword = self.request.GET.get('kw', '')  # 'kw' 파라미터에서 검색어 가져오기
        logger.info(f"검색어: {search_keyword}")  # 검색어 로깅
        post_list = self.model.objects.order_by('-create_date')  # 게시글을 생성일 기준으로 최신순 정렬

        # 검색어가 존재하고 검색 필드가 설정된 경우, 해당 검색어로 필터링합니다.
        if search_keyword and self.search_fields:
            query = Q()  # 복합 쿼리 생성을 위한 Q 객체 생성
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': search_keyword})  # 검색 필드 내에서 검색어가 포함된 항목을 필터링
            post_list = post_list.filter(query).distinct()  # 중복된 게시글 제거
        
        return post_list  # 필터링된 게시글 QuerySet 반환

    def get_context_data(self, **kwargs) -> dict:
        """
        get_context_data 메서드는 템플릿에 전달할 추가 데이터를 설정합니다.

        페이지 번호, 검색어, 게시글 인덱스 등을 템플릿에 전달합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출

        # 현재 페이지 번호와 검색어를 컨텍스트에 추가
        context['page'] = self.request.GET.get('page', '1')  # 현재 페이지 번호 설정
        context['kw'] = self.request.GET.get('kw', '')  # 검색어 설정

        # 페이지 인덱스 계산
        page_obj = context['paginator'].get_page(context['page'])  # 페이지네이션 객체에서 현재 페이지 가져오기
        """
        현재 페이지에서 몇 번째 글부터 시작하는지를 결정하는 값이 start_index입니다. 
        예를 들어, 페이지 1에서 게시글의 start_index()는 1번부터 시작하고, 
        페이지 2에서는 21번부터 시작하는 식입니다.
        """
        start_index = page_obj.start_index()  # 현재 페이지의 시작 인덱스 계산
        total_post_count = context['paginator'].count  # 전체 글 개수 가져오기
        post_indices = [(total_post_count - (start_index - 1) - i, obj) for i, obj in enumerate(page_obj.object_list)]  # 게시글 인덱스와 객체를 리스트로 만듦
        context['post_indices'] = post_indices  # 게시글 인덱스를 역순으로 설정
        
        return context  # 추가 데이터를 포함한 컨텍스트 반환


class BaseFormMixin(LoginRequiredMixin, BaseExtraContextMixin):
    """
    BaseFormMixin 클래스는 게시글 또는 댓글을 생성하거나 수정할 때 사용할 공통 폼 믹스인입니다.

    이미지 업로드와 기본 폼 처리 로직을 포함합니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 지정합니다. 하위 클래스에서 설정이 필요합니다.
        
    form_class : Form
        사용할 폼 클래스를 지정합니다. 하위 클래스에서 설정이 필요합니다.
        
    template_name : str
        사용할 템플릿 파일의 경로를 지정합니다.

    Methods
    -------
    get_context_data(**kwargs):
        템플릿에 전달할 추가 데이터를 설정합니다.
    
    _save_uploaded_images(obj):
        업로드된 이미지를 객체에 저장합니다.
    
    form_valid(form):
        폼이 유효한 경우 객체를 저장하고, 작성자 및 생성일/수정일을 설정합니다.
    """
    
    model = NotImplemented  # 사용할 모델 지정 (하위 클래스에서 설정 필요)
    form_class = None  # 사용할 폼 클래스 (하위 클래스에서 설정 필요)
    template_name = None  # 사용할 템플릿 (하위 클래스에서 설정 필요)

    def get_context_data(self, **kwargs) -> dict:
        """
        템플릿에서 사용할 이미지 URL을 설정하는 메서드입니다.

        예를 들어, 수정 시에 이미 업로드된 이미지가 있을 경우 이를 템플릿에 전달합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자(템플릿에서 변수로 사용할 수 있는 모든 데이터)입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출
        # comment에 image1과 image2 필드가 있는지 확인
        image1_url = self.object.image1.url if hasattr(self.object, 'image1') and self.object.image1 else None
        image2_url = self.object.image2.url if hasattr(self.object, 'image2') and self.object.image2 else None
        
        # 이미 업로드된 이미지가 있으면 그 URL을 템플릿에 전달
        context['initial_image1_url'] = (
            self.object.image1.url if self.object and image1_url else None
        )
        context['initial_image2_url'] = (
            self.object.image2.url if self.object and image2_url else None
        )
        return context  # 추가 데이터를 포함한 컨텍스트 반환

    def _save_uploaded_images(self, obj):
        """
        업로드된 이미지를 객체에 저장하는 메서드입니다.

        이미지가 업로드된 경우에만 저장합니다.

        Parameters
        ----------
        obj : Model instance
            저장할 모델 인스턴스입니다.

        Returns
        -------
        None
        """
        if 'image1' in self.request.FILES:  # 이미지1이 업로드된 경우
            obj.image1 = self.request.FILES['image1']
        if 'image2' in self.request.FILES:  # 이미지2가 업로드된 경우
            obj.image2 = self.request.FILES['image2']

    def form_valid(self, form):
        """
        폼이 유효한 경우 객체를 저장하는 메서드입니다.

        작성자를 현재 사용자로 설정하고, 객체가 새로 생성된 경우 생성일을,
        수정된 경우 수정일을 설정합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        obj : Model instance
            저장된 모델 인스턴스입니다.
        """
        obj = form.save(commit=False)  # 객체 저장을 지연시킴
        if not obj.pk:  # 새로 생성된 경우
            obj.author = self.request.user  # 작성자를 현재 사용자로 설정
            obj.create_date = timezone.now()  # 생성일 설정
        else:  # 기존 객체를 수정하는 경우
            obj.modify_date = timezone.now()  # 수정일 설정

        self._save_uploaded_images(obj)  # 업로드된 이미지 저장
        obj.save()  # 객체 저장
        
        return obj  # 저장된 객체 반환


class BaseCreateView(BaseFormMixin, CreateView):
    """
    BaseCreateView 클래스는 게시글 또는 댓글을 생성하는 기본 뷰입니다.

    로그인한 사용자만 접근할 수 있으며, 폼을 처리하고 댓글인 경우에는 해당 댓글 위치로 이동합니다.

    Methods
    -------
    form_valid(form):
        폼이 유효한 경우 객체를 생성하고, 댓글인 경우 해당 댓글 위치로 리다이렉트합니다.
    """

    def form_valid(self, form):
        """
        폼이 유효한 경우 객체를 생성하는 메서드입니다.

        댓글인 경우 해당 댓글 위치로 이동할 수 있도록 앵커를 추가합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            생성된 객체의 상세 페이지로 리다이렉트합니다.
        """
        obj = super().form_valid(form)  # BaseFormMixin의 form_valid 호출
        
        # 댓글인지 게시글인지에 따라 메시지 태그 설정
        if hasattr(obj, 'post'):
            extra_tags = f'comment {obj.pk}'  # 댓글이면 'comment {id}' 형식으로 태그 설정
        else:
            extra_tags = f'post'
        
        messages.success(self.request, '성공적으로 작성되었습니다.', extra_tags=extra_tags)
        
        # 댓글인 경우 해당 위치로 이동하도록 앵커 추가
        if hasattr(obj, 'post'):
            return redirect(f"{reverse(self.success_url, kwargs={'pk': obj.post.pk})}#comment-{obj.pk}")
        return redirect(reverse(self.success_url, kwargs={'pk': obj.pk}))


class BaseReadView(DetailView):
    """
    BaseReadView는 게시글의 상세 내용을 보여주는 공통 뷰입니다.

    게시글과 댓글에 대한 상세 정보를 보여줍니다.

    Attributes
    ----------
    model : Model
        사용할 모델을 지정합니다. 하위 클래스에서 설정 필요.
        
    template_name : str
        사용할 템플릿 파일의 경로를 지정합니다. 하위 클래스에서 설정 필요.
        
    context_object_name : str
        템플릿에서 사용할 객체의 이름을 지정합니다.

    Methods
    -------
    get_context_data(**kwargs):
        게시글의 댓글 및 작성자 여부 등의 추가 데이터를 템플릿에 전달합니다.
    
    _process_comments(comments):
        각 댓글에 대해 작성자 여부 및 AI 처리 여부를 추가합니다.
    
    _get_comment_messages(comments):
        각 댓글에 연결된 메시지를 가져옵니다.
    """
    model = NotImplemented  # 사용할 모델 지정 (하위 클래스에서 설정 필요)
    template_name = NotImplemented  # 사용할 템플릿 지정 (하위 클래스에서 설정 필요)
    context_object_name = 'post'  # 템플릿에서 사용할 객체 이름

    def get_context_data(self, **kwargs) -> dict:
        """
        get_context_data 메서드는 게시글과 그에 대한 댓글 정보를 템플릿에 전달합니다.

        작성자가 현재 사용자인지 여부와 댓글 정보를 설정합니다.

        Parameters
        ----------
        kwargs : dict
            템플릿에 전달할 추가적인 키워드 인자(템플릿에서 변수로 사용할 수 있는 모든 데이터)입니다.

        Returns
        -------
        dict
            템플릿에 전달할 추가적인 데이터를 포함한 컨텍스트 딕셔너리입니다.
        """
        context = super().get_context_data(**kwargs)  # 부모 클래스의 get_context_data 호출
        post = self.get_object()  # 현재 게시글 가져오기
        comments = post.comments.all()  # 게시글에 달린 모든 댓글 가져오기

        # 작성자가 현재 사용자인지 여부와 댓글 정보 추가
        context['is_author'] = self.request.user == post.author
        
        # 댓글 및 메시지 처리
        context['processed_comments'] = self._process_comments(comments)
        
        return context  # 추가 데이터를 포함한 컨텍스트 반환

    def _process_comments(self, comments) -> list:
        """
        _process_comments 메서드는 각 댓글에 대해 작성자 여부 및 AI 처리 여부를 추가하고, 
        
        메시지(django.messages)를 연결합니다.

        Parameters
        ----------
        comments : QuerySet
            처리할 댓글들의 QuerySet입니다.

        Returns
        -------
        list
            처리된 댓글 목록을 리스트 형태로 반환합니다.
        """
        processed_comments = []  # 처리된 댓글을 저장할 리스트
        comment_messages = self._get_comment_messages(comments)  # 각 댓글에 연결된 메시지 가져오기

        # 각 댓글을 처리하여 필요한 정보를 추가
        for comment in comments:
            is_author = self.request.user == comment.author  # 현재 사용자가 댓글 작성자인지 여부
            is_ai_processing = (comment.content == "AI가 처리 중입니다." and comment.author.username == "AI")  # AI 처리 여부 확인
            
            # comment에 image1과 image2 필드가 있는지 확인
            image1_url = comment.image1.url if hasattr(comment, 'image1') and comment.image1 else None
            image2_url = comment.image2.url if hasattr(comment, 'image2') and comment.image2 else None
            
            processed_comments.append({
                'id': comment.id,
                'content': comment.content,
                'is_author': is_author,
                'is_ai_processing': is_ai_processing,
                'image1': image1_url,
                'image2': image2_url,
                'modify_date': comment.modify_date,
                'author_username': comment.author.username,
                'create_date': comment.create_date,
                'voter_count': comment.voter.count(),
                'messages': comment_messages.get(str(comment.id), [])  # 해당 댓글의 메시지 추가
            })
        return processed_comments  # 처리된 댓글 리스트 반환

    def _get_comment_messages(self, comments) -> dict:
        """
        _get_comment_messages 메서드는 각 댓글에 연결된 메시지를 가져옵니다.

        Parameters
        ----------
        comments : QuerySet
            메시지를 연결할 댓글들의 QuerySet입니다.

        Returns
        -------
        dict
            댓글 ID를 키로 하여 메시지를 리스트로 저장한 딕셔너리입니다.
        """
        comment_messages = {str(comment.id): [] for comment in comments}  # 댓글 ID로 초기화된 딕셔너리
        for message in messages.get_messages(self.request):
            for comment in comments:
                # message.tags에 comment.id가 있는지 확인 
                # massage.tags 설정은 각 해위하는 뷰(예 : voteview) 에서 extra_tags 로 설정
                if str(comment.id) in message.tags:  
                    comment_messages[str(comment.id)].append({
                        'text': message.message,
                        'tags': message.tags,
                    })
        return comment_messages  # 댓글 메시지 딕셔너리 반환


class BaseUpdateView(BaseFormMixin, UpdateView):
    """
    BaseUpdateView 클래스는 게시글 또는 댓글을 수정하는 기본 뷰입니다.

    수정 후에는 댓글인 경우 해당 댓글 위치로 리다이렉트하며, 성공 메시지를 표시합니다.

    Attributes
    ----------
    extra_tags_byME : str
        메시지 태그에 추가할 문자열입니다.

    Methods
    -------
    form_valid(form):
        폼이 유효한 경우 객체를 수정하고, 댓글인 경우 해당 댓글 위치로 리다이렉트합니다.
    """

    extra_tags_byME = 'post'  # 기본 메시지 태그 설정

    def form_valid(self, form):
        """
        폼이 유효한 경우 객체를 수정하는 메서드입니다.

        댓글인 경우 해당 댓글 위치로 이동하도록 앵커를 추가하고, 성공 메시지를 표시합니다.

        Parameters
        ----------
        form : Form
            유효성을 통과한 폼 인스턴스입니다.

        Returns
        -------
        HttpResponseRedirect
            수정된 객체의 상세 페이지로 리다이렉트합니다.
        """
        obj = super().form_valid(form)  # BaseFormMixin의 form_valid 호출

        # 댓글인지 게시글인지에 따라 메시지 태그 설정
        if hasattr(obj, 'post'):
            extra_tags = f'comment {obj.pk}'  # 댓글이면 'comment {id}' 형식으로 태그 설정
        else:
            extra_tags = f'post'
        
        # 이미지 부분이 수정되었다면 
        if 'image1' in self.request.FILES or 'image2' in self.request.FILES:
            messages.success(self.request, '수정시에는 AI 기능을 제공하지 않습니다.', extra_tags=extra_tags)
            
        messages.success(self.request, '성공적으로 수정되었습니다.', extra_tags=extra_tags)

        # 댓글인 경우 해당 위치로 이동하도록 앵커 추가
        if hasattr(obj, 'post'):
            return redirect(f"{reverse(self.success_url, kwargs={'pk': obj.post.pk})}#comment-{obj.pk}")
        return redirect(reverse(self.success_url, kwargs={'pk': obj.pk}))


class BaseDeleteView(LoginRequiredMixin, DeleteView):
    """
    BaseDeleteView 클래스는 게시글 또는 댓글을 삭제하는 기본 뷰입니다.

    삭제 후에는 성공 메시지를 표시하고, 지정된 URL로 리다이렉트합니다.

    Methods
    -------
    get(request, *args, **kwargs):
        GET 요청이 들어오면 삭제 로직을 바로 실행합니다.
    
    delete(request, *args, **kwargs):
        작성자만 객체를 삭제할 수 있도록 처리하고, 삭제 후 성공 메시지를 표시합니다.
    """

    def get(self, request, *args, **kwargs):
        """
        GET 요청이 들어오면 삭제 로직을 바로 실행하는 메서드입니다.

        Parameters
        ----------
        request : HttpRequest
            현재 요청 객체입니다.

        Returns
        -------
        HttpResponse
            삭제 결과에 따른 리다이렉트 응답입니다.
        """
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        객체를 삭제하는 메서드입니다.

        작성자만 삭제할 수 있으며, 삭제 후 성공 메시지를 표시하고 지정된 URL로 리다이렉트합니다.

        Parameters
        ----------
        request : HttpRequest
            현재 요청 객체입니다.

        Returns
        -------
        HttpResponse
            삭제 후 리다이렉트 응답입니다.
        """
        obj = self.get_object()  # 삭제할 객체 가져오기

        # 작성자 권한 확인
        if request.user != obj.author:
            extra_tags = 'comment' if hasattr(obj, 'post') else 'post'
            messages.error(request, '삭제 권한이 없습니다.', extra_tags=extra_tags)
            return redirect(reverse(self.success_url, kwargs={'pk': obj.pk if hasattr(obj, 'post') else obj.pk}))

        # 객체 삭제
        obj.delete()

        # 댓글인지 게시글인지에 따라 메시지 태그 설정
        # 삭제는 앵커가 필요고 해당 댓글 부분에 메시지를 출력 할 수 없으므로 일반적인 'post' 태그로 설정
        extra_tags = f'post'

        content = '댓글' if hasattr(obj, 'post') else '게시글'
        # 성공 메시지
        messages.success(request, f'성공적으로 {content} 삭제했습니다.', extra_tags=extra_tags)

        # 리다이렉트
        if hasattr(obj, 'post'):
            return redirect(reverse(self.success_url, kwargs={'pk': obj.post.pk}))
        return redirect(reverse(self.success_url))


class BaseVoteView(LoginRequiredMixin, RedirectView):
    """
    BaseVoteView 클래스는 게시글 또는 댓글에 대해 추천하는 기능을 담당하는 뷰입니다.

    사용자는 자신이 작성한 글이나 댓글은 추천할 수 없으며, 추천 상태에 따라 추천을 추가하거나 취소합니다.

    Methods
    -------
    get_redirect_url(*args, **kwargs):
        추천 로직을 처리한 후, 추천이 완료된 후 리다이렉트할 URL을 반환합니다.
    """

    model = NotImplemented  # 사용할 모델 지정 (하위 클래스에서 설정 필요)
    success_url = NotImplemented  # 리다이렉트할 URL 지정 (하위 클래스에서 설정 필요)

    def get_redirect_url(self, *args, **kwargs) -> str:
        """
        추천 로직을 처리한 후 리다이렉트할 URL을 반환하는 메서드입니다.

        게시글인지 댓글인지에 따라 적절한 메시지와 앵커를 설정합니다.

        Parameters
        ----------
        args : list
            URL 경로에 사용할 추가 인자입니다.
        kwargs : dict
            URL 경로에 사용할 추가 키워드 인자입니다.

        Returns
        -------
        str
            추천 후 리다이렉트할 URL 문자열입니다.
        """
        obj = get_object_or_404(self.model, pk=kwargs['pk'])  # 추천할 객체 가져오기
        
        # 댓글인지 게시글인지에 따라 메시지 태그 설정
        if hasattr(obj, 'post'):
            extra_tags = f'comment {obj.pk}'  # 댓글이면 'comment {id}' 형식으로 태그 설정
        else:
            extra_tags = f'post'

        # 추천 로직 처리
        if self.request.user == obj.author:
            messages.error(self.request, '본인이 작성한 항목은 추천할 수 없습니다.', extra_tags=extra_tags)
        elif self.request.user in obj.voter.all():
            obj.voter.remove(self.request.user)  # 이미 추천한 경우 추천 취소
            messages.success(self.request, '추천을 취소했습니다.', extra_tags=extra_tags)
        else:
            obj.voter.add(self.request.user)  # 추천하지 않은 경우 추천 추가
            messages.success(self.request, '추천하였습니다.', extra_tags=extra_tags)

        # 댓글이면 해당 댓글 위치로 이동할 수 있도록 앵커 추가
        if hasattr(obj, 'post'):
            return f"{reverse(self.success_url, kwargs={'pk': obj.post.pk})}#comment-{obj.pk}"
        return reverse(self.success_url, kwargs={'pk': obj.pk})

