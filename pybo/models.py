from django.db import models
from django.contrib.auth.models import User

# ==========================
# Question 모델 (질문 데이터)
# ==========================
class Question(models.Model):
    """
    질문 데이터를 저장하는 모델입니다.
    
    Attributes:
        author (ForeignKey): 질문 작성자 (User 모델과 다대일 관계).
        subject (CharField): 질문 제목, 최대 200자.
        content (TextField): 질문 내용.
        create_date (DateTimeField): 질문 작성일시.
        modify_date (DateTimeField): 질문 수정일시, null 값을 허용.
        view_count (PositiveIntegerField): 질문 조회수, 기본값은 0.
        voter (ManyToManyField): 질문을 추천한 사용자들, ManyToMany 관계.
        image1 (ImageField): 질문에 첨부된 첫 번째 이미지, null과 빈 값을 허용.
        image2 (ImageField): 질문에 첨부된 두 번째 이미지, null과 빈 값을 허용.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200, blank=False)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    voter = models.ManyToManyField(User, related_name='voter_question')
    image1 = models.ImageField(upload_to='pybo/image1/', null=True, blank=True, verbose_name='업로드 이미지1')
    image2 = models.ImageField(upload_to='pybo/image2/', null=True, blank=True, verbose_name='업로드 이미지2')
    
    def __str__(self):
        return self.title

# ==========================
# Answer 모델 (답변 데이터)
# ==========================
class Answer(models.Model):
    """
    답변 데이터를 저장하는 모델입니다.
    
    Attributes:
        author (ForeignKey): 답변 작성자 (User 모델과 다대일 관계).
        question (ForeignKey): 답변이 달린 질문, 질문이 삭제되면 답변도 함께 삭제됨.
        content (TextField): 답변 내용.
        create_date (DateTimeField): 답변 작성일시.
        modify_date (DateTimeField): 답변 수정일시, null 값을 허용.
        voter (ManyToManyField): 답변을 추천한 사용자들, ManyToMany 관계.
        answer_image (ImageField): 답변에 첨부된 이미지, null과 빈 값을 허용.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')
    answer_image = models.ImageField(upload_to='pybo/answer_image', null=True, blank=True, verbose_name='업로드 이미지')
    
    def __str__(self):
        return self.title
    
# ========================== 일단 보류 ==========================

# from django.db import models
# from django.contrib.auth.models import User
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey

# # ==========================
# # Board 모델 (공통 게시판 데이터)
# # ==========================
# class Board(models.Model):
#     """
#     게시판의 공통 필드를 정의한 모델입니다.
#     다양한 게시판 유형(질문, 공지사항 등)에 연결할 수 있습니다.
    
#     Attributes:
#         author (ForeignKey): 게시글 작성자 (User 모델과 다대일 관계).
#         content (TextField): 게시글 내용.
#         create_date (DateTimeField): 게시글 작성일시.
#         modify_date (DateTimeField): 게시글 수정일시, null 값을 허용.
#         view_count (PositiveIntegerField): 게시글 조회수, 기본값은 0.
#         content_type (ForeignKey): 연결된 모델의 타입 (Question, Answer 등).
#         object_id (PositiveIntegerField): 연결된 모델의 ID.
#         content_object (GenericForeignKey): 연결된 객체 (Question, Answer 등).
#     """
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     create_date = models.DateTimeField()
#     modify_date = models.DateTimeField(null=True, blank=True)
#     view_count = models.PositiveIntegerField(default=0)

#     # Generic Foreign Key를 위한 필드
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')

#     def __str__(self):
#         return f'{self.content_type} - {self.author}'

# # ==========================
# # Question 모델 (질문 데이터)
# # ==========================
# class Question(models.Model):
#     """
#     질문 데이터를 저장하는 모델입니다.
    
#     Attributes:
#         author (ForeignKey): 질문 작성자 (User 모델과 다대일 관계).
#         subject (CharField): 질문 제목, 최대 200자.
#         content (TextField): 질문 내용.
#         create_date (DateTimeField): 질문 작성일시.
#         modify_date (DateTimeField): 질문 수정일시, null 값을 허용.
#         view_count (PositiveIntegerField): 질문 조회수, 기본값은 0.
#         voter (ManyToManyField): 질문을 추천한 사용자들, ManyToMany 관계.
#         image1 (ImageField): 질문에 첨부된 첫 번째 이미지, null과 빈 값을 허용.
#         image2 (ImageField): 질문에 첨부된 두 번째 이미지, null과 빈 값을 허용.
#     """
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
#     subject = models.CharField(max_length=200, blank=False)
#     content = models.TextField()
#     create_date = models.DateTimeField()
#     modify_date = models.DateTimeField(null=True, blank=True)
#     view_count = models.PositiveIntegerField(default=0)
#     voter = models.ManyToManyField(User, related_name='voter_question')
#     image1 = models.ImageField(upload_to='pybo/image1/', null=True, blank=True, verbose_name='업로드 이미지1')
#     image2 = models.ImageField(upload_to='pybo/image2/', null=True, blank=True, verbose_name='업로드 이미지2')
    
#     def __str__(self):
#         return self.subject


# # ==========================
# # Answer 모델 (답변 데이터)
# # ==========================
# class Answer(models.Model):
#     """
#     답변 데이터를 저장하는 모델입니다.
    
#     Attributes:
#         author (ForeignKey): 답변 작성자 (User 모델과 다대일 관계).
#         question (ForeignKey): 답변이 달린 질문, 질문이 삭제되면 답변도 함께 삭제됨.
#         content (TextField): 답변 내용.
#         create_date (DateTimeField): 답변 작성일시.
#         modify_date (DateTimeField): 답변 수정일시, null 값을 허용.
#         voter (ManyToManyField): 답변을 추천한 사용자들, ManyToMany 관계.
#         answer_image (ImageField): 답변에 첨부된 이미지, null과 빈 값을 허용.
#     """
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     content = models.TextField()
#     create_date = models.DateTimeField()
#     modify_date = models.DateTimeField(null=True, blank=True)
#     voter = models.ManyToManyField(User, related_name='voter_answer')
#     answer_image = models.ImageField(upload_to='pybo/answer_image', null=True, blank=True, verbose_name='업로드 이미지')
    
#     def __str__(self):
#         return self.question.subject


