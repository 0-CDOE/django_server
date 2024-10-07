from django import forms
from pybo.models import SimilarityPost, SimilarityComment, DetectionPost, DetectionComment


class SimilarityPostForm(forms.ModelForm):
    # # 커스텀 필드 정의
    # DETECTOR_CHOICES = [
    #     ('dlib', 'Dlib'),
    #     ('yolo', 'YOLO'),
    #     ('mtcnn', 'MTCNN'),
    # ]
    
    # PREDICTOR_CHOICES = [
    #     ('fairface', 'FairFace'),
    #     ('yolo_turmp', 'Find President'),
    # ]
    
    # # 탐지기(Detectors) 체크박스 필드
    # detectors = forms.MultipleChoiceField(
    #     choices=DETECTOR_CHOICES,
    #     widget=forms.CheckboxSelectMultiple,
    #     label='탐지기 (Detectors)',
    #     required=False
    # )
    
    # # 예측기(Predictors) 체크박스 필드
    # predictors = forms.MultipleChoiceField(
    #     choices=PREDICTOR_CHOICES,
    #     widget=forms.CheckboxSelectMultiple,
    #     label='예측기 (Predictors)',
    #     required=False
    # )

    class Meta:
        model = SimilarityPost
        fields = ['subject', 'content', 'image1', 'image2']  # 기존 필드

        labels = {
            'subject': '제목',
            'content': '내용',
            'image1': '이미지1',
            'image2': '이미지2',
        }


class SimilarityCommentForm(forms.ModelForm):
    class Meta:
        model = SimilarityComment  # 이 폼이 Answer 모델과 연결됨
        fields = ['content', 'image1', 'image2']  # 사용할 필드 (답변 내용, 첨부 이미지)
        
        # 각 필드에 표시될 라벨을 정의
        labels = {
            'content': '답변내용',
            'image1': '이미지1',
            'image2': '이미지2',
        }

class DetectionPostForm(forms.ModelForm):
    # 커스텀 필드 정의
    DETECTOR_CHOICES = [
        ('dlib', 'Dlib'),
        ('yolo', 'YOLO'),
        ('mtcnn', 'MTCNN'),
    ]
    
    PREDICTOR_CHOICES = [
        ('fairface', 'FairFace'),
    ]
    
    # 탐지기(Detectors) 체크박스 필드
    detectors = forms.MultipleChoiceField(
        choices=DETECTOR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='탐지기 (Detectors)',
        required=False
    )
    
    # 예측기(Predictors) 체크박스 필드
    predictors = forms.MultipleChoiceField(
        choices=PREDICTOR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='예측기 (Predictors)',
        required=False
    )

    class Meta:
        model = DetectionPost
        fields = ['subject', 'content', 'image1']
        
        labels = {
            'subject': '제목',
            'content': '내용',
            'image1': '이미지1',
        }

class DetectionCommentForm(forms.ModelForm):
    class Meta:
        model = DetectionComment
        fields = ['content', 'image1']
        
        labels = {
            'content': '댓글내용',
            'image1': '이미지1',
        }