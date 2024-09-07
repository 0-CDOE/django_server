from django.db import models
from django.contrib.auth.models import User

# Question 모델은 질문 데이터를 저장하는 모델입니다.
class Question(models.Model):
    # 질문 작성자, User 모델과 다대일 관계
    # on_delete=models.CASCADE: User가 삭제되면 해당 사용자의 질문도 함께 삭제
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    
    # 질문 제목, 최대 200자까지 허용, 반드시 입력해야 함
    subject = models.CharField(max_length=200, blank=False)
    
    # 질문 내용, 비워둘 수 없음
    content = models.TextField()
    
    # 질문 작성 일시
    create_date = models.DateTimeField()
    
    # 질문 수정 일시, 수정하지 않으면 null
    modify_date = models.DateTimeField(null=True, blank=True)
    
    # 질문 조회 수, 기본값은 0
    view_count = models.PositiveIntegerField(default=0)
    
    # 질문을 추천한 사용자들, 여러 사용자가 추천 가능 (ManyToManyField)
    voter = models.ManyToManyField(User, related_name='voter_question')
    
    # 질문에 첨부된 이미지, 이미지를 비워둘 수 있음
    question_image = models.ImageField(upload_to='question_images/', null=True, blank=True, verbose_name='업로드 이미지')

    # 객체를 문자열로 표현할 때 제목을 반환
    def __str__(self):
        return self.subject

# Answer 모델은 질문에 대한 답변 데이터를 저장하는 모델입니다.
class Answer(models.Model):
    # 답변 작성자, 작성자가 삭제되면 답변도 삭제됨
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    
    # 답변이 달린 질문과 연결, 질문이 삭제되면 답변도 삭제됨
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # 답변 내용
    content = models.TextField()
    
    # 답변 작성 일시
    create_date = models.DateTimeField()
    
    # 답변 수정 일시, 수정하지 않으면 null
    modify_date = models.DateTimeField(null=True, blank=True)
    
    # 답변을 추천한 사용자들, 여러 사용자가 추천 가능 (ManyToManyField)
    voter = models.ManyToManyField(User, related_name='voter_answer')
    
    # 답변에 첨부된 이미지, 이미지를 비워둘 수 있음
    answer_image = models.ImageField(upload_to='answer_image/', null=True, blank=True, verbose_name='업로드 이미지')

    # 객체를 문자열로 표현할 때 제목을 반환
    def __str__(self):
        return self.question.subject

# Comment 모델은 질문 또는 답변에 대한 댓글 데이터를 저장하는 모델입니다.
class Comment(models.Model):
    # 댓글 작성자, 작성자가 삭제되면 댓글도 삭제됨
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 댓글 내용
    content = models.TextField()
    
    # 댓글 작성 일시
    create_date = models.DateTimeField()
    
    # 댓글 수정 일시, 수정하지 않으면 null
    modify_date = models.DateTimeField(null=True, blank=True)
    
    # 질문에 달린 댓글, 질문과 댓글의 관계, 비워둘 수 있음
    question = models.ForeignKey(Question, null=True, blank=True, related_name='comments', on_delete=models.CASCADE)
    
    # 답변에 달린 댓글, 비워둘 수 있음
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    
    # 부모 댓글 (대댓글 기능), 비워둘 수 있음
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)

    # 객체를 문자열로 표현할 때 댓글 내용의 앞 20자를 반환
    def __str__(self):
        return self.content[:20]
