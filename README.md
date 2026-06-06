# 커피 원두 추천 앱

오픈소스소프트웨어실습 기말과제 - Streamlit + FastAPI + Docker + EC2 통합 추천 앱.

사용자의 커피 취향(산미·바디·로스팅·향·단맛·카페인·추출방식)을 입력받아
원두 데이터베이스(12종)와 가중치 점수화 매칭으로 TOP3 원두를 추천한다.

## 구성

```
coffee-bean-recommender/
├─ front/                     Streamlit 프론트엔드
│  ├─ app.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ back/                      FastAPI 백엔드
│  ├─ main.py
│  ├─ beans.json              원두 DB
│  ├─ Dockerfile
│  └─ requirements.txt
├─ docker-compose.yml
└─ .gitignore
```

- Streamlit (front) : 사용자 입력 폼 + 추천 결과 카드 표시
- FastAPI (back)    : `/recommend` 엔드포인트로 입력 받아 점수화 → JSON 응답
- 두 컨테이너는 Docker 네트워크로 연결되며 Streamlit이 `http://back:8000`으로 호출

## 로컬 실행

```bash
docker compose up -d --build
# 브라우저에서 http://localhost 접속
```

중지:

```bash
docker compose down
```

## EC2 배포

EC2 인스턴스에 SSH 접속 후:

```bash
git clone <repo URL>
cd <repo 폴더>
docker compose up -d --build
docker ps
```

EC2 **보안 그룹 인바운드 규칙에 TCP 80 허용** 필수.

브라우저에서 `http://<EC2 퍼블릭 IP>` 접속.

## 동작 흐름

1. Streamlit 화면에서 7가지 취향 입력 (산미 / 바디 / 로스팅 / 향 / 단맛 / 카페인 / 추출방식)
2. "원두 추천받기" 버튼 클릭
3. Streamlit이 FastAPI `/recommend` 엔드포인트에 POST 요청
4. FastAPI가 입력값을 100점 만점 가중치 점수화 → 원두 DB와 매칭하여 TOP3 선정
5. Streamlit이 JSON 응답을 받아 카드 형태로 결과 출력
   (원두명, 산지, 매칭 점수, 풍미 노트, 매칭 이유, 추출 팁)

## 점수 기준 (100점 만점)

| 항목 | 배점 |
|---|---|
| 산미 매칭 | 20 |
| 바디 매칭 | 20 |
| 향 프로파일 매칭 | 20 |
| 로스팅 매칭 | 15 |
| 단맛 매칭 | 10 |
| 카페인 매칭 | 10 |
| 추출 방식 매칭 | 5 |

## 컨테이너 자동 재시작

`docker-compose.yml`의 `restart: always` 정책으로 Docker 데몬 또는 EC2 인스턴스가
재시작되더라도 두 컨테이너가 자동으로 다시 기동된다.
