from background_task import background
import httpx
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os
from django.conf import settings
import base64
import platform
import mimetypes

from ..models import DetectionCommentModel, DetectionPostModel, SimilarityCommentModel, SimilarityPostModel
from ..url_patterns import URLS

import logging
logger = logging.getLogger(URLS['APP_NAME'])

def get_image_paths(post):
    """
    게시글의 이미지 경로를 운영체제에 맞게 처리하여 반환합니다.
    
    Parameters
    ----------
    post : DetectionPostModel
        게시글 객체입니다.
    
    Returns
    -------
    tuple
        운영체제에 맞게 처리된 이미지 경로들 (image1_path, image2_path)
    """
    image1_path = post.image1.path if hasattr(post, 'image1') else None 
    image2_path = post.image2.path if hasattr(post, 'image2') else None

    # 운영체제에 맞게 경로 처리
    if platform.system() == "Windows":
        image1_path = image1_path.replace("/", "\\")
        if image2_path:
            image2_path = image2_path.replace("/", "\\")
    else:
        image1_path = image1_path.replace("\\", "/")
        if image2_path:
            image2_path = image2_path.replace("\\", "/")
    
    return image1_path, image2_path

def save_processed_image(data, django_dir, comment):
    """
    AI 처리 결과로 받은 이미지를 파일로 저장하고, 댓글에 경로를 업데이트합니다.

    Parameters
    ----------
    data : dict
        AI 서버에서 받은 처리 결과 JSON 데이터입니다.
    django_dir : str
        Django 프로젝트의 BASE_DIR 경로입니다.
    comment : DetectionCommentModel
        댓글 객체입니다.
    
    Returns
    -------
    None
    """
    # 서버에서 받은 경로 처리
    str_path = data['image_path']
    result_image = data['base64_image']
    result_text = data['message']

    # 운영체제에 따른 경로 처리
    if platform.system() == "Windows":
        result_image_path = os.path.join('media', str_path.split('media\\', 1)[-1])
        db_path = str_path.split('media\\', 1)[-1]
    else:
        result_image_path = os.path.join('media', str_path.split('media/', 1)[-1])
        db_path = str_path.split('media/', 1)[-1]

    # 이미지를 디코딩하여 저장
    decode_image = base64.b64decode(result_image)
    results_folder = os.path.join(django_dir, result_image_path)

    with open(results_folder, 'wb') as out_file:
        out_file.write(decode_image)

    # 댓글 업데이트
    comment.content = result_text
    comment.image1 = db_path
    comment.save()

@background(schedule=1)
def detect_president_DBT(board_name: str, post_id: int, comment_id: int) -> None:
    """
    게시글에 첨부된 이미지를 AI 서버로 전송하여 처리 결과를 댓글로 업데이트하는 백그라운드 태스크입니다.
    게시글과 댓글 정보를 바탕으로 AI 처리를 예약하고 결과를 댓글에 저장합니다.

    Parameters
    ----------
    board_name : str
        게시판의 이름입니다. AI 처리 로그에 사용됩니다.

    post_id : int
        처리할 게시글의 ID입니다.

    comment_id : int
        처리 결과를 저장할 댓글의 ID입니다.

    Returns
    -------
    None
    """
    post_model = DetectionPostModel
    comment_model = DetectionCommentModel
    
    logger.info(f"AI 처리 중 - Board:{board_name} ID: {post_id}")

    # 게시글과 댓글 조회
    post = get_object_or_404(post_model, pk=post_id)
    comment = get_object_or_404(comment_model, pk=comment_id)

    # 이미지 경로 조회
    image1_path, _ = get_image_paths(post)

    try:
        # AI 서버로 이미지 전송
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            with open(image1_path, 'rb') as f:
                ai_server = URLS['AI_SERVER']['local']
                files = {'file': f}
                response = client.post(f"{ai_server}/detect_president/", files=files)

        django_dir = settings.BASE_DIR

        if response.status_code == 200:  # AI 서버에서 응답 성공
            data = response.json()

            # AI 처리 결과 저장
            save_processed_image(data, django_dir, comment)

            logger.info(f"AI 처리 완료 - Board:{board_name} ID: {post_id}")

        else:
            # AI 처리 실패 시 오류 메시지 댓글에 저장
            comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
            comment.modify_date = timezone.now()
            comment.save()

    except Exception as e:
        # AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()
        comment.save()

@background(schedule=1)
def compare_similarity_DBT(board_name: str, post_id: int, comment_id: int) -> None:
    """
    두 이미지를 AI 서버로 전송하여 유사도 분석 결과를 댓글로 업데이트하는 백그라운드 태스크입니다.

    Parameters
    ----------
    board_name : str
        게시판의 이름입니다.

    post_id : int
        처리할 게시글의 ID입니다.

    comment_id : int
        처리 결과를 저장할 댓글의 ID입니다.

    Returns
    -------
    None
    """
    post_model = SimilarityPostModel
    comment_model = SimilarityCommentModel
    
    logger.info(f"AI 처리 중 - Board:{board_name} ID: {post_id}")

    # 댓글 및 게시글 조회
    comment = get_object_or_404(comment_model, pk=comment_id)
    post = get_object_or_404(post_model, pk=post_id)

    # 두 이미지 경로 조회
    image1_path, image2_path = get_image_paths(post)

    # 이미지 타입 추정
    img1_type = mimetypes.guess_type(image1_path)
    img2_type = mimetypes.guess_type(image2_path)

    try:
        # AI 서버로 이미지 전송 및 결과 받기
        with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            with open(image1_path, 'rb') as f1, open(image2_path, 'rb') as f2:
                ai_server = URLS['AI_SERVER']['local']
                
                files = {
                    'file1': (os.path.basename(image1_path), f1, img1_type[0]),
                    'file2': (os.path.basename(image2_path), f2, img2_type[0])
                }
                
                response = client.post(f"{ai_server}/compare_similarity/", files=files)

        if response.status_code == 200:
            result = response.json()

            # AI 처리 결과를 댓글에 저장
            comment.content = result.get('result', 'AI 처리 중 오류가 발생했습니다.')
            comment.save()

            logger.info(f"AI 처리 완료 - Board:{board_name} ID: {post_id}")

    except ValueError as e:
        # 처리 중 문제가 발생한 경우 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = str(e)
        comment.modify_date = timezone.now()
        comment.save()

    except Exception as e:
        # 기타 AI 처리 실패 시 예외 처리
        logger.exception(f"AI 처리 실패 - Board:{board_name} ID: {post_id}")
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()
        comment.save()
