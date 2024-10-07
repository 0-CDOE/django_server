from django import forms
from pybo.models import SimilarityPost, SimilarityComment, DetectionPost, DetectionComment


class SimilarityPostForm(forms.ModelForm):
    """
    SimilarityPost 모델과 연결된 폼을 정의하는 클래스입니다.

    이 폼을 통해 사용자는 제목, 내용, 이미지1, 이미지2를 입력할 수 있습니다.

    Attributes
    ----------
    model : SimilarityPost
        이 폼이 연결된 모델은 SimilarityPost 모델입니다.
        
    fields : list
        폼에서 입력받을 필드 목록입니다. ['subject', 'content', 'image1', 'image2']를 입력받습니다.

    labels : dict
        각 필드에 표시될 라벨을 정의한 딕셔너리입니다.
    """
    
    class Meta:
        model = SimilarityPost  # 폼이 연결된 모델 설정
        fields = ['subject', 'content', 'image1', 'image2']  # 사용할 필드 지정
        labels = {
            'subject': '제목',
            'content': '내용',
            'image1': '이미지1',
            'image2': '이미지2',
        }


class SimilarityCommentForm(forms.ModelForm):
    """
    SimilarityComment 모델과 연결된 폼을 정의하는 클래스입니다.

    이 폼을 통해 사용자는 댓글 내용과 두 개의 이미지를 입력할 수 있습니다.

    Attributes
    ----------
    model : SimilarityComment
        이 폼이 연결된 모델은 SimilarityComment 모델입니다.
        
    fields : list
        폼에서 입력받을 필드 목록입니다. ['content', 'image1', 'image2']를 입력받습니다.

    labels : dict
        각 필드에 표시될 라벨을 정의한 딕셔너리입니다.
    """
    
    class Meta:
        model = SimilarityComment  # 폼이 연결된 모델 설정
        fields = ['content', 'image1', 'image2']  # 사용할 필드 지정
        labels = {
            'content': '답변내용',  # 라벨: 'content' 필드는 "답변내용"으로 표시됨
            'image1': '이미지1',  # 라벨: 'image1' 필드는 "이미지1"로 표시됨
            'image2': '이미지2',  # 라벨: 'image2' 필드는 "이미지2"로 표시됨
        }


class DetectionPostForm(forms.ModelForm):
    """
    DetectionPost 모델과 연결된 폼을 정의하는 클래스입니다.

    이 폼을 통해 사용자는 제목, 내용, 이미지1을 입력할 수 있습니다.

    Attributes
    ----------
    model : DetectionPost
        이 폼이 연결된 모델은 DetectionPost 모델입니다.
        
    fields : list
        폼에서 입력받을 필드 목록입니다. ['subject', 'content', 'image1']를 입력받습니다.

    labels : dict
        각 필드에 표시될 라벨을 정의한 딕셔너리입니다.
    """
    
    class Meta:
        model = DetectionPost  # 폼이 연결된 모델 설정
        fields = ['subject', 'content', 'image1']  # 사용할 필드 지정
        labels = {
            'subject': '제목',  # 라벨: 'subject' 필드는 "제목"으로 표시됨
            'content': '내용',  # 라벨: 'content' 필드는 "내용"으로 표시됨
            'image1': '이미지1',  # 라벨: 'image1' 필드는 "이미지1"로 표시됨
        }


class DetectionCommentForm(forms.ModelForm):
    """
    DetectionComment 모델과 연결된 폼을 정의하는 클래스입니다.

    이 폼을 통해 사용자는 댓글 내용과 이미지1을 입력할 수 있습니다.

    Attributes
    ----------
    model : DetectionComment
        이 폼이 연결된 모델은 DetectionComment 모델입니다.
        
    fields : list
        폼에서 입력받을 필드 목록입니다. ['content', 'image1']를 입력받습니다.

    labels : dict
        각 필드에 표시될 라벨을 정의한 딕셔너리입니다.
    """
    
    class Meta:
        model = DetectionComment  # 폼이 연결된 모델 설정
        fields = ['content', 'image1']  # 사용할 필드 지정
        labels = {
            'content': '댓글내용',  # 라벨: 'content' 필드는 "댓글내용"으로 표시됨
            'image1': '이미지1',  # 라벨: 'image1' 필드는 "이미지1"로 표시됨
        }
