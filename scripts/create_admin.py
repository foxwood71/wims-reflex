
import sys
import os
import asyncio

import reflex as rx
from sqlmodel import select

# [추가] 스크립트의 상위 폴더(프로젝트 루트)를 파이썬 경로에 추가합니다.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#  프로젝트의 모델과 유틸리티를 가져옵니다.
import rxconfig  # noqa: F401, E402
from wims.domains.usr.models import User, UserRole  # noqa: E402
from wims.utils import get_password_hash  # noqa: E402
#  rxconfig를 임포트하여 DB 설정을 로드합니다.


async def create_admin_user():
    """
    관리자 계정을 생성하는 비동기 함수
    """
    #  로그인 ID와 비밀번호를 여기서 설정하세요.
    ADMIN_LOGIN_ID = "admin"
    ADMIN_PASSWORD = "admin_password"  # <-- 원하는 비밀번호로 변경하세요!

    print("관리자 계정 생성을 시작합니다...")

    #  rx.session을 사용하여 데이터베이스에 연결합니다.
    with rx.session() as session:
        #  이미 해당 아이디의 사용자가 있는지 확인합니다.
        existing_user = session.exec(
            select(User).where(User.login_id == ADMIN_LOGIN_ID)
        ).one_or_none()

        if existing_user:
            print(f"이미 '{ADMIN_LOGIN_ID}' 사용자가 존재합니다. 생성을 건너뜁니다.")
            return

        #  비밀번호를 안전하게 해싱합니다.
        hashed_password = get_password_hash(ADMIN_PASSWORD)

        #  새로운 관리자 사용자 객체를 만듭니다.
        new_admin = User(
            login_id=ADMIN_LOGIN_ID,
            password_hash=hashed_password,
            email="admin@example.com",  # 원하는 이메일로 변경 가능
            name="관리자",
            role=UserRole.ADMIN,  # 역할을 ADMIN으로 설정
            is_active=True,
        )

        #  세션에 추가하고 데이터베이스에 저장(commit)합니다.
        session.add(new_admin)
        session.commit()

        print("=" * 30)
        print("🎉 관리자 계정이 성공적으로 생성되었습니다! 🎉")
        print(f"   - 아이디: {ADMIN_LOGIN_ID}")
        print(f"   - 비밀번호: {ADMIN_PASSWORD}")
        print("=" * 30)
        print("이제 'reflex run'으로 앱을 실행하고 로그인하세요.")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
