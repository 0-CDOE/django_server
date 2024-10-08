from ..core.config import PipelineStep

class InfoDrawer(PipelineStep):
    """
    얼굴 인식 결과(바운딩 박스 및 텍스트)를 이미지에 그려넣는 파이프라인 단계입니다.

    이 클래스는 얼굴 인식 예측 결과를 사용하여 이미지에 바운딩 박스와 주석(성별, 대상 여부 등)을 표시합니다.
    """

    def __init__(self, thickness=2):
        """
        InfoDrawer 클래스를 초기화합니다.

        Args:
            thickness (int, optional): 바운딩 박스의 두께. 기본값은 2입니다.
        """
        self.thickness = thickness

    def process(self, data):
        """
        이미지에 얼굴 박스와 텍스트 주석을 그려넣습니다.

        Args:
            data (object): 파이프라인 데이터 객체로, 이미지와 얼굴 예측 결과를 포함해야 합니다.
                           'image_rgb' 속성에 이미지가 포함되어 있으며,
                           'predictions' 속성에 얼굴 박스, 성별, 대상 여부 등의 정보가 포함되어야 합니다.

        Returns:
            object: 주석이 추가된 이미지가 포함된 데이터 객체. 'image_rgb' 속성이 업데이트됩니다.
        """
        
        # 이미지 처리 유틸리티 인스턴스 가져오기
        utils = data.image_utils

        # 원본 이미지 가져오기 ('image_rgb' 속성에서 이미지 데이터를 불러옴)
        image_rgb = data.image_rgb

        # 얼굴 예측 정보 가져오기 ('predictions' 속성에서 얼굴 박스, 성별, 대상 여부 정보)
        predictions = data.predictions
        face_boxes = predictions['face_boxes']  # 얼굴 박스 좌표 리스트
        is_target_list = predictions.get('is_target', [False] * len(face_boxes))  # 대상 여부 리스트, 기본값 False
        gender_list = predictions.get('gender', ['남성'] * len(face_boxes))  # 성별 리스트, 기본값 남성

        # 각 얼굴 박스에 대해 반복 처리
        for index, face in enumerate(face_boxes):
            # 얼굴 박스 좌표 추출
            x1, y1, x2, y2 = face  

            # 성별 정보 가져오기 (리스트 범위를 벗어나지 않도록 처리)
            gender = gender_list[index] if index < len(gender_list) else '남성'

            # 성별에 따라 박스 색상 결정 (남성: 파랑색, 여성: 빨간색)
            box_color = (50, 100, 255) if gender == '남성' else (255, 100, 50)

            # 대상 여부에 따른 텍스트 설정 (대상일 경우 '가카!' 텍스트 추가)
            text = '가카!' if is_target_list[index] else ''

            # 이미지에 텍스트 추가 (한글 텍스트 주석)
            image_rgb = utils.draw_korean_text(
                image=image_rgb,
                text=text,
                position=(x1, y1),  # 텍스트를 그릴 위치 (얼굴 박스 좌상단)
                font_size=15,
                font_color=(0, 0, 0),  # 텍스트 색상 (검은색)
                background_color=box_color  # 텍스트 배경 색상 (성별에 따른 박스 색상)
            )

            # 얼굴 박스 그리기 (박스 좌표와 색상, 두께 설정)
            utils.draw_rectangle(
                image=image_rgb,
                coordinates=(x1, y1, x2, y2),
                color=box_color,
                thickness=self.thickness
            )

        # 주석이 추가된 이미지를 데이터 객체에 저장
        data.image_rgb = image_rgb

        # 처리된 데이터 객체 반환 (다음 파이프라인 단계로 전달)
        return data
