# /wims_project/wims/models/__init__.py

# flake8: noqa
#  SQLModel을 여기서 임포트하여 다른 곳에서 쉽게 사용할 수 있도록 합니다.
from sqlmodel import SQLModel

#  각 도메인 모델 파일에서 모든 모델 클래스를 임포트합니다.
from wims.domains.usr.models import * 

print("All models imported successfully!")  #  제대로 임포트되는지 확인용