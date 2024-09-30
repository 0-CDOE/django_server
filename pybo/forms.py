from django import forms
from pybo.models import Question, Answer,Comment,Question_Free,Answer_Free

########################################################################################################

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'content', 'image1','image2'] # subject와 content 필드만 사용 #내용없애고 image만 추가
        labels = {

            'subject': '제목',
            'content' :'내용',
            'image1' : '이미지1',
            'image2' : '이미지2',
        }
        
########################################################################################################

class QuestionFreeForm(forms.ModelForm):
    class Meta:
        model = Question_Free
        fields = ['subject', 'content', 'image1']  # subject와 content 필드만 사용 #내용없애고 image만 추가
        labels = {

            'subject': '제목',
            'content': '내용',
            'image1': '이미지1',
            
        }


########################################################################################################

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }

########################################################################################################

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content','parent']

        labels ={
            'content': '내용',
        }

    def __init__(self, *args, **kwargs):
        self.parent_comment = kwargs.pop('parent_comment', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.parent_comment:
            comment.parent = self.parent_comment
        if commit:
            comment.save()
        return comment

########################################################################################################