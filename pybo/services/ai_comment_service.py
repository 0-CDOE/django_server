from django.utils import timezone
from django.contrib.auth.models import User
from ..url_patterns import URLS

import logging
logger = logging.getLogger(URLS['APP_NAME'])

class AICommentService:
    """
    AICommentService 클래스는 게시글에 대한 AI 댓글 생성과 AI 탐지 작업을 처리하는 서비스입니다.

    Attributes
    ----------
    post : post_model
        게시글 모델 인스턴스입니다. AI 댓글을 달 게시글을 나타냅니다.

    comment_model : comment_model
        댓글 모델입니다. 생성된 AI 댓글이 저장될 모델입니다.

    board_name : str
        현재 게시판의 이름입니다. AI 처리 작업을 예약할 때 사용됩니다.

    comment : comment_model, optional
        생성된 댓글을 저장하는 변수입니다. AI 탐지 작업에서 이 댓글을 업데이트합니다.

    Methods
    -------
    get_ai_user() -> User or None
        AI 계정을 가져옵니다. AI 계정이 존재하지 않을 경우 로그에 오류를 남기고 None을 반환합니다.

    create_comment() -> bool
        AI 댓글을 생성합니다. 생성 성공 시 True, 실패 시 False를 반환합니다.

    detect_president() -> bool
        AI 탐지 작업을 예약합니다. 성공 시 True, 실패 시 False를 반환합니다.
    """

    def __init__(self, post, comment_model, board_name):
        """
        AICommentService 클래스의 생성자입니다.

        Parameters
        ----------
        post : post_model
            게시글 모델 인스턴스입니다. AI 댓글을 달 게시글을 나타냅니다.

        comment_model : comment_model
            댓글 모델입니다. 생성된 AI 댓글이 저장될 모델입니다.

        board_name : str
            현재 게시판의 이름입니다. AI 처리 작업을 예약할 때 사용됩니다.
        """
        self.post = post
        self.comment_model = comment_model
        self.board_name = board_name
        self.comment = None

    def get_ai_user(self):
        """
        AI 계정을 가져오는 메서드입니다. 'AI'라는 사용자명을 가진 계정을 조회합니다.

        Returns
        -------
        User or None
            AI 사용자 계정을 반환합니다. 계정이 없을 경우 None을 반환하고 오류를 로그에 기록합니다.
        """
        try:
            return User.objects.get(username='AI')
        except User.DoesNotExist:
            logger.error("AI 계정이 존재하지 않습니다.")
            return None

    def create_comment(self) -> bool:
        """
        AI 댓글을 생성하는 메서드입니다. AI가 게시글을 처리 중임을 나타내는 초기 댓글을 생성합니다.

        Returns
        -------
        bool
            댓글 생성에 성공하면 True, 실패하면 False를 반환합니다.
        """
        ai_user = self.get_ai_user()
        if ai_user is None:
            return False
        
        try:
            # AI가 처리 중임을 나타내는 초기 댓글 생성
            comment = self.comment_model(
                post=self.post,
                author=ai_user,
                content="AI가 처리 중입니다.",
                create_date=timezone.now(),
            )
            comment.save()

            # 성공적으로 생성된 댓글을 인스턴스 변수로 저장
            self.comment = comment
            
            # 로그에 성공 메시지 기록
            logger.info(f"초기 AI 답변 생성됨 - 게시글 ID: {self.post.id}")
            return True
        except Exception as e:
            # 댓글 생성 실패 시 로그에 오류 메시지 기록
            logger.error(f"AI 댓글 생성 실패 - 게시글 ID: {self.post.id}, 에러: {str(e)}")
            return False

    def detect_president(self) -> bool:
        """
        AI 탐지 작업을 예약하는 메서드입니다. 이 메서드는 백그라운드에서 AI가 게시글 이미지를 처리하도록 예약합니다.

        Returns
        -------
        bool
            AI 작업 예약에 성공하면 True, 실패하면 False를 반환합니다.
        """
        from ..tasks.task import detect_president_DBT
        try:
            # 백그라운드 작업으로 AI 탐지 예약
            detect_president_DBT(
                board_name=self.board_name,
                post_id=self.post.id,
                comment_id=self.comment.id
            )
            logger.info(f"AI 처리 예약됨 - 게시글 ID: {self.post.id}")
            return True
        except Exception as e:
            # AI 탐지 예약 실패 시 로그에 오류 메시지 기록
            logger.error(f"AI 처리 실패 - 게시글 ID: {self.post.id}, 에러: {str(e)}")
            return False

    def compare_similarity(self):
        """
        두 게시글의 유사도를 비교하는 메서드입니다.

        Parameters
        ----------
        post1 : post_model
            비교할 게시글 모델 인스턴스입니다.

        post2 : post_model
            비교할 게시글 모델 인스턴스입니다.

        Returns
        -------
        float
            두 게시글의 유사도를 0~1 사이의 값으로 반환합니다.
        """
        # 두 게시글의 이미지를 비교하는 로직
        from ..tasks.task import compare_similarity_DBT
        try:
            # 백그라운드 작업으로 AI 탐지 예약
            compare_similarity_DBT(
                board_name=self.board_name,
                post_id=self.post.id,
                comment_id=self.comment.id
            )
            logger.info(f"AI 처리 예약됨 - 게시글 ID: {self.post.id}")
            return True
        except Exception as e:
            # AI 탐지 예약 실패 시 로그에 오류 메시지 기록
            logger.error(f"AI 처리 실패 - 게시글 ID: {self.post.id}, 에러: {str(e)}")
            return False