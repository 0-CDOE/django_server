# main.py
import face_recognition
import logging
import pickle
import numpy as np
import os
from django.conf import settings  # settings.py 파일의 설정을 사용하기 위한 임포트
import logging  # 로그 출력을 위한 모듈

logger = logging.getLogger('pybo')  # 'pybo'라는 로거 생성

# 각 단계별 클래스를 개별적으로 임포트합니다.
from ai_system import Pipeline, Data, BaseConfig, steps, factories

def process_image1(image_path, selected_detectors):
    """
    메인 함수로, 전체 파이프라인을 구성하고 실행합니다.
    """
    # 설정 정보를 가져옵니다.
    config = BaseConfig.get_config()

    # 탐지기(detectors) 생성
    detectors = []
    for detector in selected_detectors:
        if detector == 'mtcnn':
            continue
        detectors.append(factories.FaceDetectorFactory.create(detector, config[f'{detector}']))

    # 파이프라인 설정
    pipeline = Pipeline()
    pipeline.add(steps.FaceDetector(detectors))                    
    pipeline.add(steps.FaceEncoder())                           
    
    logging.info(f"이미지 처리 시작: {image_path}")
    
    # 데이터 객체를 생성하여 이미지 경로를 설정합니다.
    data = Data(config, image_path)
    data.image_rgb
    
    # 파이프라인을 실행하여 이미지를 처리합니다.
    pipeline.run(data)
    
    logging.info(f"이미지 처리 완료: {image_path}")
    output_image_path = data.output_image_path
    encodings = data.encodings
    return output_image_path, encodings

def compare_faces(image1_path, image2_path, selected_detectors=['yolo']):
    """
    두 이미지의 얼굴을 비교하여 일치 여부를 판별합니다.
    """
    logger.info(f"이미지1 인코딩 중: {image1_path}")
    # 이미지1 처리
    _ , encoding1 = process_image1(image1_path, selected_detectors)
    logger.info(f"이미지2 인코딩 중: {image2_path}")
    # 이미지2 처리
    _ , encoding2 = process_image1(image2_path, selected_detectors)
    # 유사도 계산   
    
    if len(encoding1) != 1:
        raise ValueError("1 사진에 얼굴이 1개가 아닙니다.")
    elif len(encoding2) != 1:
        raise ValueError("2 사진에 얼굴이 1개가 아닙니다.")

    logger.info(f"얼굴 유사도 계산 중: {image1_path}, {image2_path}")
    simiarity = float(face_recognition.face_distance(np.array(encoding1), np.array(encoding2))) * 100
        
    return simiarity

class DetectionConfig(BaseConfig):
    # 별도로 추가할 커스터마이징이 없으면 그대로 사용
    yolo_path = 'yolov8_l_trump.pt'
    django_dir = settings.BASE_DIR
    results_folder = os.path.join(django_dir, 'media', 'detection', 'a_image1')

def process_image2(image_path, selected_detectors=['yolo']):
    """
    메인 함수로, 전체 파이프라인을 구성하고 실행합니다.
    """
    # 설정 정보를 가져옵니다.
    config = DetectionConfig.get_config()

    # 탐지기(detectors) 생성
    detectors = []
    for detector in selected_detectors:
        if detector == 'mtcnn':
            continue
        detectors.append(factories.FaceDetectorFactory.create(detector, config[f'{detector}']))
        
    # 파이프라인 설정
    pipeline = Pipeline()
    pipeline.add(steps.FaceDetector(detectors))
    pipeline.add(steps.InfoDrawer(thickness=5))    
    pipeline.add(steps.Saver())
    
    logging.info(f"이미지 처리 시작: {image_path}")
    
    # 데이터 객체를 생성하여 이미지 경로를 설정합니다.
    data = Data(config, image_path)
    data.image_rgb
    
    # 파이프라인을 실행하여 이미지를 처리합니다.
    pipeline.run(data)
    
    logging.info(f"이미지 처리 완료: {image_path}")
    output_image_path = data.output_image_path
    return output_image_path