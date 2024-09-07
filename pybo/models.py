from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 모델을 변경한 후에는 반드시 makemigrations와 migrate를 통해 데이터베이스를 변경해 주어야 한다.

# Question 모델은 질문 데이터를 저장할 때 사용하는 모델이다.
class Question(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='author_question'
        ) # User 모델은 회원 가입시 데이터 저장에 사용했던 모델이다.
    
    subject = models.CharField(max_length=200, blank=False) # CharField는 길이 제한이 있는 문자열을 정의할 때 사용
    content = models.TextField(null=True, blank=True) # 공백허용으로 변경 y.h.kang
    
    #content = models.TextField() # TextField는 길이 제한이 없는 문자열을 정의할 때 사용
    
    create_date = models.DateTimeField() # DateTimeField는 날짜와 시간을 의미
    """
    null=True는 데이터베이스에 해당 값이 NULL로 저장되는 것을 허용
    
    blank=True는 폼 데이터 검사 시 값이 없어도 된다는 것을 의미
    
    즉, modify_date는 수정일시를 저장하는 필드이며, 수정일시가 없을 수도 있다는 의미
    """
    modify_date = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    voter = models.ManyToManyField( User,related_name='voter_question') # 추천인 추가
    image = models.ImageField(upload_to='image/', null=True, blank=True, verbose_name='업로드 이미지')
    image2 = models.ImageField(upload_to='image2/', null=True, blank=True, verbose_name='업로드 이미지2')

    # __str__ 메서드는 객체를 문자열로 표현할 때 사용하는 함수이다.
    def __str__(self):
        return self.subject

# Answer 모델은 답변 데이터를 저장할 때 사용하는 모델이다.
class Answer(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='author_answer'
        ) 
    """
    ForeignKey는 다른 모델과의 연결, 다대일 관계를 정의해주는 클래스 
    
    on_delete=models.CASCADE는 연결된 객체가 삭제될 때 이 객체와 연결된 객체도 삭제된다는 의미
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, related_name='comments', on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
