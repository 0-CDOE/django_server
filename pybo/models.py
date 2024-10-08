from django.db import models
from django.contrib.auth.models import User


class AbstractPost(models.Model):
    """
    게시글의 공통 필드를 정의한 추상화된 게시글 모델입니다.

    이 클래스는 다른 게시글 모델에서 상속하여 사용할 수 있습니다.
    실제로 데이터베이스에 저장되지 않으며, 공통 필드를 묶어 재사용할 수 있습니다.

    Attributes
    ----------
    author : ForeignKey
        게시글 작성자 (User 모델과 다대일 관계).
    subject : CharField
        게시글 제목, 최대 200자.
    content : TextField
        게시글 내용.
    create_date : DateTimeField
        게시글 작성일시, 처음 생성될 때 자동으로 기록됩니다.
    modify_date : DateTimeField
        게시글 수정일시, null 값을 허용하며, 수정 시 변경됩니다.
    view_count : PositiveIntegerField
        게시글 조회수, 기본값은 0입니다.
    voter : ManyToManyField
        게시글을 추천한 사용자들, 다대다 관계.
    """
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    voter = models.ManyToManyField(User, related_name='voter_%(class)s')

    class Meta:
        abstract = True  # 이 모델은 실제 데이터베이스 테이블로 생성되지 않음 (추상 클래스)

    def __str__(self) -> str:
        """
        게시글의 제목을 반환합니다.

        Returns
        -------
        str
            게시글의 제목을 나타내는 문자열입니다.
        """
        return self.subject


class AbstractComment(models.Model):
    """
    댓글의 공통 필드를 정의한 추상화된 댓글 모델입니다.

    이 클래스는 다른 댓글 모델에서 상속하여 사용할 수 있습니다.
    실제로 데이터베이스에 저장되지 않으며, 공통 필드를 묶어 재사용할 수 있습니다.

    Attributes
    ----------
    author : ForeignKey
        댓글 작성자 (User 모델과 다대일 관계).
    content : TextField
        댓글 내용.
    create_date : DateTimeField
        댓글 작성일시, 처음 생성될 때 자동으로 기록됩니다.
    modify_date : DateTimeField
        댓글 수정일시, null 값을 허용하며, 수정 시 변경됩니다.
    voter : ManyToManyField
        댓글을 추천한 사용자들, 다대다 관계.
    """
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_%(class)s')

    class Meta:
        abstract = True  # 이 모델은 실제 데이터베이스 테이블로 생성되지 않음 (추상 클래스)

    def __str__(self) -> str:
        """
        댓글 내용을 반환합니다. (최대 20자까지 표시)

        Returns
        -------
        str
            댓글 내용을 나타내는 문자열입니다.
        """
        return f"댓글: {self.content[:20]}"  # 댓글 내용의 앞 20자를 반환


class SimilarityPostModel(AbstractPost):
    """
    얼굴 유사도 비교 게시판의 게시글 모델입니다.

    얼굴 유사도를 비교하기 위해 두 개의 이미지를 첨부할 수 있습니다.

    Attributes
    ----------
    image1 : ImageField
        게시글에 첨부된 첫 번째 이미지.
    image2 : ImageField
        게시글에 첨부된 두 번째 이미지.
    """
    
    image1 = models.ImageField(upload_to='similarity/q_image1/', null=True, blank=True, verbose_name='q_image1')
    image2 = models.ImageField(upload_to='similarity/q_image2/', null=True, blank=True, verbose_name='q_image2')

    def __str__(self) -> str:
        """
        게시글 제목을 반환합니다.

        Returns
        -------
        str
            게시글 제목을 나타내는 문자열입니다.
        """
        return f"질문: {self.subject}"


class SimilarityComment(AbstractComment):
    """
    얼굴 유사도 비교 게시판의 댓글 모델입니다.

    게시글에 대한 댓글로 두 개의 이미지를 첨부할 수 있습니다.

    Attributes
    ----------
    post : ForeignKey
        댓글이 달린 게시글 (SimilarityPost 모델과 다대일 관계).
    image1 : ImageField
        댓글에 첨부된 첫 번째 이미지.
    image2 : ImageField
        댓글에 첨부된 두 번째 이미지.
    """
    
    post = models.ForeignKey(SimilarityPostModel, on_delete=models.CASCADE, related_name='comments')
    image1 = models.ImageField(upload_to='similarity/a_image1/', null=True, blank=True, verbose_name='a_image1')
    image2 = models.ImageField(upload_to='similarity/a_image2/', null=True, blank=True, verbose_name='a_image2')

    def __str__(self) -> str:
        """
        댓글 내용을 반환합니다. (최대 20자까지 표시)

        Returns
        -------
        str
            댓글 내용을 나타내는 문자열입니다.
        """
        return f"댓글: {self.content[:20]}"


class DetectionPostModel(AbstractPost):
    """
    특정 인물 찾기 게시판의 게시글 모델입니다.

    특정 인물을 찾기 위해 하나의 이미지를 첨부할 수 있습니다.

    Attributes
    ----------
    image1 : ImageField
        게시글에 첨부된 첫 번째 이미지.
    """
    
    image1 = models.ImageField(upload_to='detection/q_image1/', null=True, blank=True, verbose_name='q_image1')

    def __str__(self) -> str:
        """
        게시글 제목을 반환합니다.

        Returns
        -------
        str
            게시글 제목을 나타내는 문자열입니다.
        """
        return f"질문: {self.subject}"


class DetectionCommentModel(AbstractComment):
    """
    특정 인물 찾기 게시판의 댓글 모델입니다.

    게시글에 대한 댓글로 하나의 이미지를 첨부할 수 있습니다.

    Attributes
    ----------
    post : ForeignKey
        댓글이 달린 게시글 (DetectionPost 모델과 다대일 관계).
    image1 : ImageField
        댓글에 첨부된 이미지.
    """
    
    post = models.ForeignKey(DetectionPostModel, on_delete=models.CASCADE, related_name='comments')
    image1 = models.ImageField(upload_to='detection/a_image1/', null=True, blank=True, verbose_name='a_image1')

    def __str__(self) -> str:
        """
        댓글 내용을 반환합니다. (최대 20자까지 표시)

        Returns
        -------
        str
            댓글 내용을 나타내는 문자열입니다.
        """
        return f"댓글: {self.content[:20]}"
