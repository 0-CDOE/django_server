from django.contrib import admin
from pybo.models import SimilarityPostModel, SimilarityCommentModel, DetectionCommentModel, DetectionPostModel

# =============================
# Admin (관리자 설정)
# =============================
class SimilarityPostAdmin(admin.ModelAdmin):
    """
    Django 관리자 페이지에서 사용할 설정을 정의하는 클래스입니다.
    
    이 클래스는 관리자 페이지에서 모델 데이터를 더 쉽게 관리할 수 있도록 도와줍니다.
    특히, 'subject' 필드로 검색할 수 있는 기능을 추가합니다.
    """
    # 관리자 페이지에서 'subject' 필드 기준으로 검색할 수 있도록 설정
    search_fields = ['subject']

# 모델을 관리자 페이지에 등록하여 관리할 수 있도록 합니다.
# SimilarityPost 모델을 등록하고, 위에서 정의한 Admin 설정을 함께 적용합니다.
admin.site.register(SimilarityPostModel, SimilarityPostAdmin)

# 나머지 모델들도 동일한 방식으로 관리자 페이지에 등록할 수 있습니다.
admin.site.register(SimilarityCommentModel)
admin.site.register(DetectionCommentModel)
admin.site.register(DetectionPostModel)
