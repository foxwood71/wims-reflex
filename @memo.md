1. 데이터베이스 초기화 (매우 중요)

   로그 상단에 Warning: Database is not initialized 경고 메시지가 있습니다.
   패키지를 설치하더라도 데이터베이스에 테이블이 없으면 로그인 시 에러가 발생합니다.
   아래 명령어들을 순서대로 실행하여 데이터베이스를 설정하고 테이블을 생성해야 합니다.

Reflex 는 다중의 스키마 환경을 고려하지 않고 있기게 Reflex db 보다는 alembic을 사용해서 처리

- Reflex DB 환경 초기화 (프로젝트당 1회만 실행):

  $ reflex db init

- 데이터 모델 기반으로 마이그레이션 파일 생성:

  $ reflex db makemigrations -m "Initial database schema" (참고: migrate 메시지는 자유롭게 변경 가능합니다.)
  $ alembic revision --autogenerate -m "Initial database schema"

- 마이그레이션 파일을 DB에 적용하여 테이블 생성:
  $ reflex db migrate
  $ alembic upgrade head

2. Debug

   - 프론트엔드: 일반 터미널에서 실행 (reflex run --frontend-only)

   - 백엔드: VS Code 디버거를 통해 실행
