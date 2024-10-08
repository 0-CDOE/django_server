import os.path
from asgiref.sync import  sync_to_async

from fastapi import FastAPI, BackgroundTasks
import aiohttp
import asyncio
import httpx
from pathlib import Path
import base64
from celery import shared_task
from django.utils import timezone

@shared_task
def request_ai_process1(comment_id,question_id):


    from .models import DetectionPost, DetectionComment


    #비동기에서 동기로 동작하는 코드를 호출하면 에러
    # comment = get_object_or_404(DetectionComment, pk=comment_id)
    # post = get_object_or_404(DetectionPost, pk=question_id)
    comment = (DetectionComment.objects.get)(pk=comment_id)
    post    = (DetectionPost.objects.get)(pk=question_id)

    image_path = post.image1.path  # 게시글에 첨부된 이미지 경로 조회
    file_name = os.path.basename(image_path)
    print("image_ path =======================",image_path)
    try:
         with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = client.post("http://52.78.102.210:8007/process_ai_image/", files=files)

         print("response code : ===========", response.status_code)

         django_dir = Path(__file__).resolve().parent.parent

         if response.status_code == 200:  # ok
            print("Image uploaded successfully")
            data = response.json()

            #서버가 ubuntu이면 \가 path여서 문제 발생
            str_path = data['image_path'].replace("/","\\")
            print("str Path ",str_path)

            result_image = data['base64_image']
            result_text  = data['message']
            result_image_path = "media\\" + str_path.split("media\\",1)[-1]

            decode_image = base64.b64decode(result_image)
            results_folder = os.path.join(django_dir,result_image_path)
            print("result text  :", result_image_path, "result folder",results_folder,'resulttext:',result_text)

            with open(results_folder,'wb') as out_file:
                 out_file.write(decode_image)
                 print("file saved ok=======================")


            comment.content = result_text
            comment.image1 =results_folder
            comment.save()

    except Exception as e:
        print("Exception error :",e)
        comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
        comment.modify_date = timezone.now()
        comment.save()




@shared_task
def request_ai_process2(comment_id,question_id):

    from .models import SimilarityPost, SimilarityComment
    import mimetypes

    comment = (SimilarityComment.objects.get)(pk=comment_id)
    post = (SimilarityPost.objects.get)(pk=question_id)

    image1_path = post.image1.path  # 이미지1 경로
    image2_path = post.image2.path  # 이미지2 경로

    #similarity_percent = compare_faces(image1_path, image2_path)
    img1_type = mimetypes.guess_type(image1_path)
    img2_type = mimetypes.guess_type(image2_path)


    with open(image1_path, 'rb') as f1:
        image_bytes1 = f1.read()

    with open(image2_path, 'rb') as f2:
        image_bytes2 = f2.read()


    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
         with open(image1_path, 'rb') as f1, open(image2_path,'rb') as f2:
            response = client.post("http://52.78.102.210:8007/process_ai_image_two/",
                                   files={'file1':(image1_path,f1,img1_type[0]),'file2':(image2_path,f2,img1_type[0])})


         if response.status_code ==200:
               result = response.json()
               print("result : ", result['result'])
               comment.content = result['result']
               comment.save()
         else:

            print("Error AI process")
            comment.content = "AI 처리 중 오류가 발생했습니다. 다시 시도해 주세요."
            comment.modify_date = timezone.now()
            comment.save()


# @shared_task()
# def test_task(a: int, b : int):
#     print("test celery task222 : ", a+b)
#     return a+b