# 크로스 플랫폼 프레임워크 기반의 유명인물 영상 분석 서비스

## 1. 목표와 기능

### 1.1 목표

우선, 서비스는 사람들이 알고 접하는 것이 중요합니다. 이를 위해 먼저, 유명인물 영상 분석 서비스로 미국 대통령들과 후보를 유명 인물로 선정하여 미국 선거 관리위원회 및 기타 단체에 제공하고, 우리의 프로젝트를 알릴 수 있는 기회를 얻을 수 있습니다. 추가로 투표율과 관심도를 올릴 수 있는 효과를 낼 수 있습니다.

### 1.2 기능

- 유사도 측정 기능
- 유명인물 탐색 및 정보 제공 기능
- 두 기능을 통한 결과 AI 답글 기능
- 커뮤니티 및 상호 작용 기능
- DB 데이터 활용

### 1.3 팀 구성
<table>
   <tr>
      <th>박상준</th>
      <th>조하나</th>
      <th>이예은</th>
      <th>강유화</th>
   </tr>
   <tr>
      <td><img src="my.jpg" width="100%"></td>
      <td><img src="my.jpg" width="100%"></td>
      <td><img src="my.jpg" width="100%"></td>
      <td><img src="my.jpg" width="100%"></td>
   </tr>
</table>

## 2.1 개발 환경

### 하드웨어 사양

- CPU: Intel Core i7-4770 @ 3.40GHz
- RAM: 16GB
- GPU: 내장 그래픽 사용

### 운영체제(OS)

- Windows 10 Home (64비트, 22H2)

### IDE 및 개발도구

- IDE: VSCode
- AI 및 데이터 분석 도구: Google Colab

### 사용 언어

- Frontend: HTML, CSS, JavaScript (JS)
- Backend 및 AI: Python

### Frontend

- JS 라이브러리: jQuery
- CSS 라이브러리: Bootstrap

### Backend

- Web Server: NGINX
- WSGI Server: gunicorn
- WAS (Python Web Framework): Django
- DB: PostgreSQL

### AI 모델 및 데이터 분석

- Python 라이브러리: OpenCV, TensorFlow, PyTorch, ultralytics, MTCNN 등
- AI 모델: YOLO, MTCNN, ResNet34 등

### 배포환경

- 플랫폼: AWS Lightsail
- 운영체제: Ubuntu 가상머신 (EC2)

### 형상관리

- Git, GitHub

## 2.2 배포 URL

- 추후 추가 예정
- 테스트용 계정
  ```
  id : test@test.test
  pw : test11!!
  ```

## 2.3 URL 구조 (모놀리식)

### main

| App       | URL            | Views Function    | HTML File Name        | Note       |
|-----------|----------------|-------------------|-----------------------|------------|
| main      | `/`            | index             | `main/index.html`     | 인덱스 화면 |

### similarity

| App       | URL                               | Views Function    | HTML File Name                | Note        |
|-----------|-----------------------------------|-------------------|-------------------------------|-------------|
| similarity| `post/create/`                     | post_create       | `similarity/post_create.html` | 게시물 작성   |
| similarity| `post/read/<int:pk>/`              | post_read         | `similarity/post_read.html`   | 게시물 읽기   |
| similarity| `post/update/<int:pk>/`            | post_update       | `similarity/post_update.html` | 게시물 수정   |
| similarity| `post/delete/<int:pk>/`            | post_delete       | `similarity/post_delete.html` | 게시물 삭제   |
| similarity| `post/vote/<int:pk>/`              | post_vote         | `similarity/post_vote.html`   | 게시물 추천   |
| similarity| `post/list/`                       | post_list         | `similarity/post_list.html`   | 게시물 목록   |
| similarity| `comment/create/<int:pk>/`         | comment_create    | `similarity/comment_create.html` | 댓글 작성   |
| similarity| `comment/update/<int:pk>/`         | comment_update    | `similarity/comment_update.html` | 댓글 수정   |
| similarity| `comment/delete/<int:pk>/`         | comment_delete    | `similarity/comment_delete.html` | 댓글 삭제   |
| similarity| `comment/vote/<int:pk>/`           | comment_vote      | `similarity/comment_vote.html`   | 댓글 추천   |

### detection

| App       | URL                               | Views Function    | HTML File Name                | Note        |
|-----------|-----------------------------------|-------------------|-------------------------------|-------------|
| detection | `post/create/`                     | post_create       | `detection/post_create.html`  | 게시물 작성   |
| detection | `post/read/<int:pk>/`              | post_read         | `detection/post_read.html`    | 게시물 읽기   |
| detection | `post/update/<int:pk>/`            | post_update       | `detection/post_update.html`  | 게시물 수정   |
| detection | `post/delete/<int:pk>/`            | post_delete       | `detection/post_delete.html`  | 게시물 삭제   |
| detection | `post/vote/<int:pk>/`              | post_vote         | `detection/post_vote.html`    | 게시물 추천   |
| detection | `post/list/`                       | post_list         | `detection/post_list.html`    | 게시물 목록   |
| detection | `comment/create/<int:pk>/`         | comment_create    | `detection/comment_create.html` | 댓글 작성   |
| detection | `comment/update/<int:pk>/`         | comment_update    | `detection/comment_update.html` | 댓글 수정   |
| detection | `comment/delete/<int:pk>/`         | comment_delete    | `detection/comment_delete.html` | 댓글 삭제   |
| detection | `comment/vote/<int:pk>/`           | comment_vote      | `detection/comment_vote.html`   | 댓글 추천   |

### 2.4 URL 구조(마이크로식)✅

- 추후 추가 예정

## 3. 요구사항 명세와 기능 명세

- 이미지는 샘플 이미지입니다.
<img src="map.png" width="100%">

- mermaid
  
```mermaid
    sequenceDiagram
    actor User as client
    participant NGINX as NGINX
    participant Gunicorn as Gunicorn
    participant Django as Django WAS
    participant DBT as Django Background Task
    participant FastAPI as FastAPI 서버
    participant AI as AI 모델

    User->>+NGINX: 게시글 및 이미지 업로드 요청
    NGINX->>+Gunicorn: 요청 전달
    Gunicorn->>+Django: 게시글 처리 요청
    Django->>+DBT: 이미지 비동기 처리 요청
    DBT->>+FastAPI: 이미지 전송 및 AI 처리 요청
    FastAPI->>+AI: 이미지 AI 처리
    AI->>+FastAPI: 처리 완료된 이미지 반환
    FastAPI->>+Django: 처리 완료된 이미지 반환
    Django->>User: 게시글 및 처리된 이미지 저장 완료 응답
```

## 4. 프로젝트 구조와 개발 일정
### 4.1 프로젝트 구조

```
Pybo0!Code
├─ 📂.env
├─ 📂.git
├─ 📂.gitignore
├─ 📂.vscode
├─ 📂common
│  ├─ 📜admin.py
│  ├─ 📜apps.py
│  ├─ 📜forms.py
│  ├─ 📜migrations
│  ├─ 📜models.py
│  ├─ 📜tests.py
│  ├─ 📜urls.py
│  └─ 📜views.py
├─ 📂config
│  ├─ 📜asgi.py
│  ├─ settings
│  │  ├─ 📜base.py
│  │  ├─ 📜local.py
│  │  └─ 📜prod.py
│  ├─ 📜urls.py
│  └─ 📜wsgi.py
├─ 📂logs
│  └─ 📜pybo.log
├─ 📜manage.py
├─ 📂pybo
│  ├─ 📜admin.py
│  ├─ 📜apps.py
│  ├─ 📜context_processors.py
│  ├─ 📜forms.py
│  ├─ migrations
│  ├─ 📜models.py
│  ├─ 📂templatetags
│  │  ├─ 📜custom_filters.py
│  │  └─ 📜custom_tags.py
│  ├─ 📜test.py
│  ├─ 📜urls.py
│  ├─ 📜url_patterns.py
│  ├─ 📂views
│  │  ├─ 📜base_views.py
│  │  ├─ 📜detection_comment_views.py
│  │  ├─ 📜detection_post_views.py
│  │  ├─ 📜similarity_comment_views.py
│  └─ └─ 📜similarity_post_views.py
├─ 📜README.md
├─ 📂static
├─ 📂templates
│  ├─ 📜base.html
│  ├─ 📜footer.html
│  ├─ 📜form_errors.html
│  ├─ 📜sidebar.html
│  ├─ 📜topbar.html
│  ├─ 📂common
│  │  ├─ 📜404.html
│  │  ├─ 📜login.html
│  │  └─ 📜signup.html
│  ├─ 📂pybo
│  │  ├─ 📜answer_list.html
│  │  ├─ 📜index.html
│  │  ├─ 📜question_detail.html
│  │  ├─ 📜question_form.html
│  └─ └─ 📜question_list.html
├─ 📂temps
└─ 📂txt
   ├─ 📜requirements.txt
   └─ 📜requirements_for_server.txt
```

### 4.1 개발 일정(WBS)
* 아래 일정표는 머메이드로 작성했습니다.
```mermaid
gantt
    title tutorial django
    dateFormat YY-MM-DD
    section 기획
        글조회(R) :2023-10-26, 1d
        글생성/수정/삭제(CUD) :2023-10-28, 1d
        로그인 기능 :2023-10-31, 1d
        검색 기능 :2023-10-31, 1d
        상세뷰 추가 구성 :2023-11-4, 1d
    section 디자인
        리디자인 :2023-11-6, 1d
    section FE
        메인    :2023-10-27, 1d
        글조회    :2023-10-27, 1d
        글등록    :2023-10-29, 2d
        글수정    :2023-10-29, 2d
        글삭제    :2023-10-29, 2d
        글검색    :2023-10-30, 1d
        로그인/로그아웃 :2023-10-31, 1d
        회원가입 페이지 :2023-11-1, 1d
        인증 접근 권한 :2023-10-31, 3d
        유저 추가 :2023-11-2, 1d
        프로필 페이지 :2023-11-5, 1d
        이미지, 조회수, 태그 추가 :2023-11-6, 1d
        댓글 추가 :2023-11-6, 1d
        리디자인 적용 :2023-11-7, 1d
    section BE
        메인    :2023-10-27, 1d
        글조회    :2023-10-27, 1d
        글등록    :2023-10-29, 2d
        글수정    :2023-10-29, 2d
        글삭제    :2023-10-29, 2d
        글검색    :2023-10-30, 1d
        로그인/로그아웃 :2023-10-31, 1d
        회원가입 페이지 :2023-11-1, 1d
        인증 접근 권한 :2023-10-31, 3d
        이미지, 조회수, 태그 :2023-11-5, 2d
        댓글 :2023-11-5, 2d
```

## 5. 역할 분담

- 팀장 : 강유화
- 박상준
- 조하나
- 이예은


## 6. 와이어프레임 / UI / BM

### 6.1 와이어프레임

- 아래 페이지별 상세 설명, 더 큰 이미지로 하나하나씩 설명 필요
- 추후 추가 예정

<img src="ui.png" width="60%">


### 6.2 화면 설계
- 화면은 gif파일로 업로드해주세요.
 
<table>
    <tbody>
        <tr>
            <td>메인</td>
            <td>로그인</td>
        </tr>
        <tr>
            <td>
      <img src="ui1.png" width="100%">
            </td>
            <td>
                <img src="ui2.png" width="100%">
            </td>
        </tr>
        <tr>
            <td>회원가입</td>
            <td></td>
        </tr>
        <tr>
            <td>
                <img src="ui3.png" width="100%">
            </td>
            <td>
                <img src="ui3.png" width="100%">
            </td>
        </tr>
        <tr>
            <td>검색</td>
            <td></td>
        </tr>
        <tr>
            <td>
                <img src="ui3.png" width="100%">
            </td>
            <td>
                <img src="ui3.png" width="100%">
            </td>
        </tr>
        <tr>
            <td></td>
            <td>글쓰기</td>
        </tr>
        <tr>
            <td>
           <img src="ui3.png" width="100%">
            </td>
            <td>
                <img src="ui3.png" width="100%">
            </td>
        </tr>
        <tr>
            <td>글 상세보기</td>
            <td>댓글</td>
        </tr>
        <tr>
            <td>
                <img src="ui3.png" width="100%">
            </td>
            <td>
                <img src="ui3.png" width="100%">
            </td>
        </tr>
    </tbody>
</table>


## 7. 데이터베이스 구조도(ERD)

```mermaid
erDiagram
    AUTH_USER {
        integer id PK
        varchar password
        datetime last_login
        boolean is_superuser
        varchar username
        varchar first_name
        varchar last_name
        varchar email
        boolean is_staff
        boolean is_active
        datetime date_joined
    }

    DETECTION_POST {
        integer id PK
        varchar subject
        text content
        datetime create_date
        datetime modify_date
        integer view_count
        varchar image1
        integer author_id FK
    }

    DETECTION_COMMENT {
        integer id PK
        text content
        datetime create_date
        datetime modify_date
        varchar image1
        integer author_id FK
        integer post_id FK
    }

    DETECTION_POST_VOTER {
        integer id PK
        integer detectionpost_id FK
        integer user_id FK
    }

    DETECTION_COMMENT_VOTER {
        integer id PK
        integer detectioncomment_id FK
        integer user_id FK
    }

    SIMILARITY_POST {
        integer id PK
        varchar subject
        text content
        datetime create_date
        datetime modify_date
        integer view_count
        varchar image1
        varchar image2
        integer author_id FK
    }

    SIMILARITY_COMMENT {
        integer id PK
        text content
        datetime create_date
        datetime modify_date
        varchar image1
        varchar image2
        integer author_id FK
        integer post_id FK
    }

    SIMILARITY_POST_VOTER {
        integer id PK
        integer similaritypost_id FK
        integer user_id FK
    }

    SIMILARITY_COMMENT_VOTER {
        integer id PK
        integer similaritycomment_id FK
        integer user_id FK
    }

    AUTH_USER ||--o{ DETECTION_POST : write
    AUTH_USER ||--o{ DETECTION_COMMENT : write
    AUTH_USER ||--o{ SIMILARITY_POST : write
    AUTH_USER ||--o{ SIMILARITY_COMMENT : write
    DETECTION_POST ||--o{ DETECTION_COMMENT : comment
    DETECTION_POST ||--o{ DETECTION_POST_VOTER : recommend
    DETECTION_COMMENT ||--o{ DETECTION_COMMENT_VOTER : recommend
    SIMILARITY_POST ||--o{ SIMILARITY_COMMENT : comment
    SIMILARITY_POST ||--o{ SIMILARITY_POST_VOTER : recommend
    SIMILARITY_COMMENT ||--o{ SIMILARITY_COMMENT_VOTER : recommend
```

## 8. Architecture

```mermaid
graph TD
    NGINX -->|Forward request| Gunicorn
    Gunicorn -->|Request to WAS| Django
    Django -->|Database request| MySQL

    Django -->|Async image processing request| DBT
    DBT -->|Send image to FastAPI for AI processing| FastAPI
    FastAPI -->|AI processing request| AI
    AI -->|Return processed image| FastAPI
    FastAPI -->|Return processed image| Django

    AWS -->|Deployment environment| NGINX
    AWS -->|Deployment environment| Gunicorn
    AWS -->|Deployment environment| Django
    AWS -->|Deployment environment| MySQL

    classDef server fill:#f9f,stroke:#333,stroke-width:2px
    classDef async fill:#9cf,stroke:#33f,stroke-width:2px,stroke-dasharray: 5, 5
    classDef cloud fill:#ff9,stroke:#f66,stroke-width:2px

    class NGINX,Gunicorn,Django,MySQL server
    class DBT,FastAPI async
    class AWS cloud
```

- 아래 Architecture 설계도는 PPT를 사용해서 작성
- 추후 작성 예정
![image](./architecture.png)

## 9. 메인 기능

- 사용자가 접속하면 메인 화면이 나오고 사이드 바에서 두개의 게시판으로 이동하거나 로그인 또는 회원 가입을 할 수 있습니다.

```mermaid
    graph TD
    User -->|접속| MainScreen[메인 화면]
    MainScreen -->|사이드 바 클릭| BoardSelection[게시판 선택]
    MainScreen -->|로그인 클릭| LoginPage[로그인 페이지]
    MainScreen -->|회원 가입 클릭| SignupPage[회원 가입 페이지]
    BoardSelection --> Board1[얼굴 유사도 비교]
    BoardSelection --> Board2[역대 대통령 찾기]
```

- 사용자가 두장의 이미지를 업로드하면 두 얼굴 간의 유사도를 비교해 줍니다.

```mermaid
stateDiagram-v2
    [*] --> 이미지업로드
    이미지업로드 --> 얼굴유사도비교중
    얼굴유사도비교중 --> 정상작동
    얼굴유사도비교중 --> 에러발생
    정상작동 --> 유사도댓글달기
    에러발생 --> 미발견댓글
    유사도댓글달기 --> [*]
    미발견댓글 --> [*]

```

- 사용자가 한장의 이미지를 업로드하면 그 중 미국의 역대 대통령이 있는지 찾아 정보글을 제공해줍니다.

```mermaid
stateDiagram-v2
    [*] --> 이미지업로드
    이미지업로드 --> 대통령찾기중
    대통령찾기중 --> 대통령발견
    대통령찾기중 --> 대통령미발견
    대통령찾기중 --> 에러발생
    대통령발견 --> 바운딩박스이미지댓글
    대통령미발견 --> 발견댓글
    에러발생 --> 미발견댓글
    바운딩박스이미지댓글 --> [*]
    발견댓글 --> [*]
    미발견댓글 --> [*]


```

## 10. 클래스 다이어 그램

## 99. 에러와 에러 해결

## 99. 개발하며 느낀점