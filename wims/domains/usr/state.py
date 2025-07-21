# /wims_project/wims/domains/usr/state.py
"""
'usr' 도메인(사용자 및 부서 관리)의 상태 및 비즈니스 로직을 정의하는 모듈입니다.
"""

import reflex as rx
from sqlmodel import select
from typing import List, Dict, Any
from ...state.base import BaseState
from .models import User, Department, UserRole
from ...utils import get_password_hash


class UserAdminState(BaseState):
    """사용자 관리 페이지의 상태와 이벤트 핸들러"""

    # [ADD] A class variable to hold the list of UserRole enum members.
    role_options: list[dict] = [
        {"value": str(role.value), "label": role.name}
        for role in UserRole
    ]
    
    #  페이지에서 사용할 상태 변수들
    users: List[User] = []
    departments: List[Department] = []
    show_modal: bool = False
    form_data: dict = {}
    is_edit: bool = False

    # [신규] UI에 표시하기 위한 데이터를 가공하는 계산된 속성
    @rx.var
    def display_users(self) -> List[Dict[str, Any]]:
        """DB에서 가져온 User 모델 리스트를 UI에 표시하기 쉬운 딕셔너리 리스트로 변환합니다."""
        user_list = []
        for user in self.users:
            user_list.append(
                {
                    "id": user.id,
                    "login_id": user.login_id,
                    "name": user.name or "",
                    "email": user.email or "",
                    "role_name": user.role.name,  # 백엔드에서는 .name 접근이 가능합니다.
                    "department_name": user.department.name if user.department else "N/A",
                    "is_active": user.is_active,
                }
            )
        return user_list

    def load_users_page(self):
        """페이지가 로드될 때 사용자 및 부서 목록을 DB에서 가져옵니다."""
        self.check_login()  #  BaseState의 로그인 확인 메서드 호출
        with rx.session() as session:
            self.users = session.exec(select(User).order_by(User.id)).all()
            self.departments = session.exec(select(Department).order_by(Department.name)).all()

    def handle_submit(self, form_data: dict):
        """사용자 생성/수정 폼 제출을 처리합니다."""
        self.form_data = form_data
        if self.is_edit:
            self.update_user()
        else:
            self.create_user()

    # [수정] open_edit_modal이 user_id를 받도록 변경
    def open_edit_modal(self, user_id: int):
        """사용자 수정 모달을 엽니다."""
        self.is_edit = True
        # ID를 사용해 DB에서 최신 사용자 정보를 가져옵니다.
        with rx.session() as session:
            user = session.get(User, user_id)
            if user:
                self.form_data = user.dict()
                self.form_data["department_id"] = str(user.department_id) if user.department_id else ""
                self.show_modal = True
            else:
                return rx.window_alert("사용자를 찾을 수 없습니다.")


    def create_user(self):
        """새로운 사용자를 생성합니다."""
        login_id = self.form_data.get("login_id")
        email = self.form_data.get("email")
        password = self.form_data.get("password")

        if not login_id or not password or not email:
            return rx.window_alert("로그인 ID, 이메일, 비밀번호는 필수입니다.")

        with rx.session() as session:
            if session.exec(select(User).where(User.login_id == login_id)).one_or_none():
                return rx.window_alert("이미 사용 중인 로그인 ID입니다.")
            if session.exec(select(User).where(User.email == email)).one_or_none():
                return rx.window_alert("이미 등록된 이메일입니다.")

            hashed_password = get_password_hash(password)
            user_data = {k: v for k, v in self.form_data.items() if k not in ["password", "id"] and v}
            
            if 'role' in user_data:
                user_data['role'] = UserRole(int(user_data['role']))
            if 'department_id' in user_data:
                user_data['department_id'] = int(user_data['department_id'])

            new_user = User(**user_data, password_hash=hashed_password)
            session.add(new_user)
            session.commit()

        self.close_and_reload("load_users_page")

    def update_user(self):
        """기존 사용자 정보를 수정합니다."""
        user_id = self.form_data.get("id")
        with rx.session() as session:
            user_to_update = session.get(User, user_id)
            if not user_to_update:
                return rx.window_alert("사용자를 찾을 수 없습니다.")

            update_data = self.form_data.copy()
            #  업데이트하지 않을 필드 제거
            update_data.pop("id", None)
            update_data.pop("login_id", None)
            update_data.pop("password", None)
            update_data.pop("created_at", None)
            update_data.pop("updated_at", None)

            for key, value in update_data.items():
                if value is not None and value != "":
                    if key == 'role':
                        value = UserRole(int(value))
                    elif key == 'department_id':
                        value = int(value)
                    setattr(user_to_update, key, value)
            
            session.add(user_to_update)
            session.commit()

        self.close_and_reload("load_users_page")

    def delete_user(self, user_id: int):
        """사용자를 삭제합니다."""
        with rx.session() as session:
            user_to_delete = session.get(User, user_id)
            if not user_to_delete:
                return rx.window_alert("사용자를 찾을 수 없습니다.")
            if user_to_delete.role == UserRole.ADMIN:
                return rx.window_alert("관리자 계정은 삭제할 수 없습니다.")

            session.delete(user_to_delete)
            session.commit()
        self.load_users_page()

    def open_create_modal(self):
        """사용자 생성 모달을 엽니다."""
        self.is_edit = False
        self.form_data = {}
        self.show_modal = True

    def open_edit_modal(self, user: User):
        """사용자 수정 모달을 엽니다."""
        self.is_edit = True
        self.form_data = user.dict()
        self.form_data["department_id"] = str(user.department_id) if user.department_id else ""
        self.show_modal = True

    def close_and_reload(self, reload_method_name: str):
        """모달을 닫고 페이지 데이터를 새로고침합니다."""
        self.show_modal = False
        self.form_data = {}
        #  getattr을 사용하여 문자열로 전달된 메서드를 호출
        getattr(self, reload_method_name)()

    # [추가] rx.dialog의 on_open_change 이벤트를 처리할 함수
    def set_show_modal(self, open: bool):
        self.show_modal = open


class DeptAdminState(BaseState):
    """부서 관리 페이지의 상태와 이벤트 핸들러"""

    #  페이지에서 사용할 상태 변수들
    departments: List[Department] = []
    show_modal: bool = False
    form_data: dict = {}
    is_edit: bool = False

    def load_depts_page(self):
        """페이지 로드 시 부서 목록을 DB에서 가져옵니다."""
        self.check_login()
        with rx.session() as session:
            self.departments = session.exec(select(Department).order_by(Department.name)).all()

    def handle_submit(self, form_data: dict):
        """부서 생성/수정 폼 제출을 처리합니다."""
        self.form_data = form_data
        if self.is_edit:
            self.update_department()
        else:
            self.create_department()

    def create_department(self):
        """새로운 부서를 생성합니다."""
        code = self.form_data.get("code")
        name = self.form_data.get("name")
        if not code or not name:
            return rx.window_alert("부서 코드와 이름은 필수입니다.")

        with rx.session() as session:
            if session.exec(select(Department).where(Department.code == code)).first():
                return rx.window_alert("이미 사용 중인 부서 코드입니다.")
            if session.exec(select(Department).where(Department.name == name)).first():
                return rx.window_alert("이미 사용 중인 부서 이름입니다.")

            dept_data = {k: v for k, v in self.form_data.items() if k != "id" and v}
            new_dept = Department(**dept_data)
            session.add(new_dept)
            session.commit()

        self.close_and_reload("load_depts_page")

    def update_department(self):
        """기존 부서 정보를 수정합니다."""
        dept_id = self.form_data.get("id")
        with rx.session() as session:
            dept_to_update = session.get(Department, dept_id)
            if not dept_to_update:
                return rx.window_alert("부서를 찾을 수 없습니다.")

            for key, value in self.form_data.items():
                if key in ["id", "code"]:
                    continue
                if value:
                    setattr(dept_to_update, key, value)

            session.add(dept_to_update)
            session.commit()

        self.close_and_reload("load_depts_page")

    def delete_department(self, dept_id: int):
        """부서를 삭제합니다."""
        with rx.session() as session:
            user_count = session.exec(select(User).where(User.department_id == dept_id)).first()
            if user_count:
                return rx.window_alert("소속된 사용자가 있어 부서를 삭제할 수 없습니다.")

            dept_to_delete = session.get(Department, dept_id)
            if dept_to_delete:
                session.delete(dept_to_delete)
                session.commit()

        self.load_depts_page()

    def open_create_modal(self):
        """부서 생성 모달을 엽니다."""
        self.is_edit = False
        self.form_data = {}
        self.show_modal = True

    def open_edit_modal(self, department: Department):
        """부서 수정 모달을 엽니다."""
        self.is_edit = True
        self.form_data = department.dict()
        self.show_modal = True
        
    def close_and_reload(self, reload_method_name: str):
        """모달을 닫고 페이지 데이터를 새로고침합니다."""
        self.show_modal = False
        self.form_data = {}
        getattr(self, reload_method_name)()

    # [추가] rx.dialog의 on_open_change 이벤트를 처리할 함수
    def set_show_modal(self, open: bool):
        self.show_modal = open