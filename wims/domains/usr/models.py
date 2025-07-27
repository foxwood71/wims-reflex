# /wims_project/wims/domains/usr/models.py
"""
'usr' 도메인의 데이터베이스 ORM 모델을 정의하는 모듈입니다.
SQLModel을 상속받는 rx.Model을 사용하여 Reflex의 상태 관리와 통합됩니다.
"""

from typing import Optional, List
from datetime import datetime, timezone
from enum import IntEnum

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Integer, Field, Relationship, Column, TIMESTAMP, func

import reflex as rx


class UserRole(IntEnum):
    """
    사용자 역할을 정의하는 정수형 Enum 클래스입니다.
    DB에는 정수 값으로 저장되지만, 코드에서는 명시적인 역할 이름으로 사용할 수 있습니다.
    """
    ADMIN = 1               # 시스템 관리자
    LAB_MANAGER = 10        # 실험실 관리자
    LAB_ANALYST = 11        # 실험 분석가
    FACILITY_MANAGER = 20   # 설비 관리자
    INVENTORY_MANAGER = 30  # 자재 관리자
    GENERAL_USER = 100      # 일반 사용자


# [추가] UI 표시에 사용할 데이터 모델
class UserList(rx.Base):
    """사용자 목록 UI에 데이터를 표시하기 위한 모델 (DB 테이블이 아님)"""
    id: int
    login_id: str
    name: str
    email: str
    role_name: str
    department_name: str
    is_active: bool


class Department(rx.Model, table=True):
    """
    PostgreSQL의 usr.departments 테이블에 매핑되는 모델.
    """
    __tablename__ = "departments"  # type: ignore
    #  PostgreSQL 스키마를 사용하는 경우 명시합니다.
    __table_args__ = {'schema': 'usr'}

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=4, unique=True, description="부서 코드 (예: HR, LAB)")
    name: str = Field(max_length=100, unique=True, description="부서명")
    notes: Optional[str] = Field(default=None, description="비고")
    sort_order: Optional[int] = Field(default=None, description="정렬 순서")
    site_list: Optional[List[int]] = Field(
        default=None, sa_column=Column(JSONB), description="관할 처리시설 목록"
    )

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now()),
        description="레코드 생성 일시"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),
        description="레코드 마지막 업데이트 일시"
    )

    #  User 모델과의 관계 설정 (한 부서에 여러 사용자가 속함)
    users: List["User"] = Relationship(back_populates="department")


class User(rx.Model, table=True):
    """
    PostgreSQL의 usr.users 테이블에 매핑되는 모델.
    """
    __tablename__ = "users"  # type: ignore
    __table_args__ = {'schema': 'usr'}

    id: Optional[int] = Field(default=None, primary_key=True)
    login_id: str = Field(max_length=50, unique=True, description="로그인 사용자명")
    password_hash: str = Field(max_length=255, description="해싱된 비밀번호")
    email: Optional[str] = Field(default=None, max_length=100, unique=True, description="사용자 이메일")
    name: Optional[str] = Field(default=None, max_length=100, description="사용자 전체 이름")\

    #  Department 모델과의 관계 설정 (한 사용자는 하나의 부서에 속함)
    department_id: Optional[int] = Field(default=None, foreign_key="usr.departments.id")

    #  UserRole Enum을 사용하여 역할 관리
    role: UserRole = Field(
        default=UserRole.GENERAL_USER,
        sa_column=Column(Integer),  # <-- 이렇게 수정하세요.
        description="사용자 역할 (권한)"
    )
    code: Optional[str] = Field(default=None, max_length=16, unique=True, description="사번 등 사용자 고유 코드")
    is_active: bool = Field(default=True, description="계정 활성 여부")

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now()),
        description="레코드 생성 일시"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()),
        description="레코드 마지막 업데이트 일시"
    )

    #  Department 모델과의 관계 설정
    department: Optional[Department] = Relationship(back_populates="users")

    # [추가] 역할(Enum)의 이름을 반환하는 계산된 속성
    @property
    def role_name(self) -> str:
        """사용자 역할의 이름을 문자열로 반환합니다."""
        return self.role.name
