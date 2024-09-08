import logging
import cv2
import os
#
from .ai_system import setup_django_system

@setup_django_system
def start_ai(request, image_path, face_recognition_system, target_encodings, selected_detectors, selected_predictors):
    # 얼굴 인식 시스템을 이용해 이미지를 처리
    output_path = face_recognition_system.process_image(image_path, target_encodings)
    #
    return output_path
    #
#