from django.db import models
from django.contrib.auth.models import User

# ==========================
# Abstract Base Post Model
# ==========================
class AbstractPost(models.Model):
    """
    게시글의 공통 필드를 정의한 추상화된 게시글 모델입니다.

    Attributes:
        author (ForeignKey): 게시글 작성자 (User 모델과 다대일 관계).
        subject (CharField): 게시글 제목, 최대 200자.
        content (TextField): 게시글 내용.
        create_date (DateTimeField): 게시글 작성일시.
        modify_date (DateTimeField): 게시글 수정일시, null 값을 허용.
        view_count (PositiveIntegerField): 게시글 조회수, 기본값은 0.
        voter (ManyToManyField): 게시글을 추천한 사용자들, ManyToMany 관계.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    voter = models.ManyToManyField(User, related_name='voter_%(class)s')

    class Meta:
        abstract = True

    def __str__(self):
        return self.subject


# ==========================
# Abstract Base Comment Model
# ==========================
class AbstractComment(models.Model):
    """
    댓글의 공통 필드를 정의한 추상화된 댓글 모델입니다.

    Attributes:
        author (ForeignKey): 댓글 작성자.
        content (TextField): 댓글 내용.
        create_date (DateTimeField): 댓글 작성일시.
        modify_date (DateTimeField): 댓글 수정일시.
        voter (ManyToManyField): 댓글을 추천한 사용자들.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_%(class)s')

    class Meta:
        abstract = True

    def __str__(self):
        return f"댓글: {self.content[:20]}"


# ==========================
# Similarity Board Post Model (얼굴 유사도 비교 게시판)
# ==========================
class SimilarityPost(AbstractPost):
    """
    얼굴 유사도 비교 게시판의 질문 모델입니다.

    Attributes:
        image1 (ImageField): 질문에 첨부된 첫 번째 이미지.
        image2 (ImageField): 질문에 첨부된 두 번째 이미지.
    """
    image1 = models.ImageField(upload_to='pybo/q_image1/', null=True, blank=True, verbose_name='q_image1')
    image2 = models.ImageField(upload_to='pybo/q_image2/', null=True, blank=True, verbose_name='q_image2')

    def __str__(self):
        return f"질문: {self.subject}"


# ==========================
# Similarity Board Comment Model (Face Similarity Board)
# ==========================
class SimilarityComment(AbstractComment):
    """
    얼굴 유사도 비교 게시판의 답변(댓글) 모델입니다.

    Attributes:
        question (ForeignKey): 해당 댓글이 달린 질문.
        image1 (ImageField): 댓글에 첨부된 첫 번째 이미지.
        image2 (ImageField): 댓글에 첨부된 두 번째 이미지.
    """
    post = models.ForeignKey(SimilarityPost, on_delete=models.CASCADE, related_name='comments')
    image1 = models.ImageField(upload_to='pybo/a_image1/', null=True, blank=True, verbose_name='a_image1')
    image2 = models.ImageField(upload_to='pybo/a_image2/', null=True, blank=True, verbose_name='a_image2')

    def __str__(self):
        return f"댓글: {self.content[:20]}"


# ==========================
# Person Detection Board Post Model (특정 인물 찾기 게시판)
# ==========================
class DetectionPost(AbstractPost):
    """
    특정 인물 찾기 게시판의 질문 모델입니다.

    Attributes:
        image1 (ImageField): 질문에 첨부된 첫 번째 이미지.
    """
    image1 = models.ImageField(upload_to='detection/q_image1/', null=True, blank=True, verbose_name='q_image1')

    def __str__(self):
        return f"질문: {self.subject}"


# ==========================
# Person Detection Board Comment Model (특정 인물 찾기 게시판)
# ==========================
class DetectionComment(AbstractComment):
    """
    특정 인물 찾기 게시판의 댓글 모델입니다.

    Attributes:
        detection (ForeignKey): 해당 댓글이 달린 질문.
        image1 (ImageField): 댓글에 첨부된 첫 번째 이미지.
    """
    detection = models.ForeignKey(DetectionPost, on_delete=models.CASCADE, related_name='comments')
    image1 = models.ImageField(upload_to='detection/a_image1/', null=True, blank=True, verbose_name='a_image1')

    def __str__(self):
        return f"댓글: {self.content[:20]}"
