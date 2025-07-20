# /reflex_user_management/app/utils.py
from passlib.context import CryptContext


#  비밀번호 해싱을 위한 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 일반 비밀번호와 데이터베이스에 저장된 해시된 비밀번호를 비교합니다.

    Args:
        plain_password (str): 사용자가 입력한 비밀번호.
        hashed_password (str): 데이터베이스에 저장된 해시.

    Returns:
        bool: 비밀번호가 일치하면 True, 그렇지 않으면 False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    입력된 비밀번호를 bcrypt 알고리즘을 사용하여 해싱합니다.

    Args:
        password (str): 해싱할 비밀번호.

    Returns:
        str: 해싱된 비밀번호 문자열.
    """
    return pwd_context.hash(password)