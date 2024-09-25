from django import forms
from pybo.models import Question, Answer

########################################################################################################

# ===================================
# QuestionForm (질문 생성 및 수정 폼)
# ===================================
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question  # 이 폼이 Question 모델과 연결됨
        fields = ['subject', 'content', 'image1', 'image2']  # 사용할 필드 (제목, 내용, 이미지1, 이미지2)
        
        # 각 필드에 표시될 라벨을 정의
        labels = {
            'subject': '제목',
            'content': '내용',
            'image1': '이미지1',
            'image2': '이미지2',
        }

########################################################################################################

# ===================================
# AnswerForm (답변 생성 및 수정 폼)
# ===================================
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer  # 이 폼이 Answer 모델과 연결됨
        fields = ['content', 'answer_image']  # 사용할 필드 (답변 내용, 첨부 이미지)
        
        # 각 필드에 표시될 라벨을 정의
        labels = {
            'content': '답변내용',
            'answer_image': '이미지',
        }

########################################################################################################