import enum
from typing import List, Dict, Any, Set

from sqlmodel import select
from sqlalchemy.orm import selectinload

import reflex as rx

from ...state.base import BaseState
from ...utils import get_password_hash

from .models import User, Department, UserRole, UserList


class UserAdminState(BaseState):
    """사용자 관리 페이지의 상태와 이벤트 핸들러"""

    # --- 상태 변수 ---
    users: list[User] = []
    show_modal: bool = False
    form_data: dict = {}
    is_edit: bool = False

    # 선택된 사용자 ID를 저장하는 집합(set)
    selected_user_ids: set[int] = set()

    # --- 클래스 변수 ---
    role_options: list[dict] = [
        {"id": str(role.value), "name": role.name}
        for role in UserRole
    ]
    department_options: list[dict] = []

    # 🔽 --- 계산된 속성 ---
    # Reflex는 상태(@rx.var)의 변경을 감지하고 UI를 업데이트합니다.
    # 때로는 딕셔너리(dict) 같은 복잡한 객체 내부의 한 가지 값이 바뀌는 것을 즉시 감지하지 못할 때가 있기에
    # @rx.var를 사용해 특정 값을 명시적으로 노출시키면, Reflex가 이 값의 변화를 항상 지켜봄
    @rx.var
    def form_role_id(self) -> str:
        return str(self.form_data.get("role", ""))

    @rx.var
    def form_department_id(self) -> str:
        return str(self.form_data.get("department_id", ""))

    # '전체' 항목이 추가된 필터 전용 목록을 생성하는 계산된 속성
    @rx.var
    def filter_department_options(self) -> list[dict]:
        """필터 드롭다운을 위한 부서 목록을 반환합니다. ('전체 부서' 포함)"""
        # '전체' 항목을 맨 앞에 추가합니다. id는 빈 문자열로 설정하여 '필터 없음'을 나타냅니다.
        return [{"id": "__all__", "name": "전체 부서"}] + self.department_options

    # 반환 타입을 명확한 UserDisplay 모델의 리스트로 변경
    @rx.var
    def display_users(self) -> List[UserList]:
        """필터링된 사용자 목록을 UserDisplay 모델의 리스트로 반환합니다."""
        user_list = []
        for user in self.users:
            user_list.append(
                UserList(
                    id=user.id,
                    login_id=user.login_id,
                    name=user.name or "",
                    email=user.email or "",
                    role_name=user.role.name,
                    department_name=user.department.name if user.department else "N/A",
                    is_active=user.is_active,
                )
            )
        return user_list

    # '전체 선택' 체크박스의 상태를 결정하는 계산된 속성
    @rx.var
    def select_all_checked_state(self) -> bool:
        """현재 표시된 모든 사용자가 선택되었는지 여부를 반환합니다. (True, False, "indeterminate")"""
        # 표시된 사용자가 없으면 체크 해제 상태
        if not self.display_users:
            return False

        # 현재 표시된 사용자의 ID 집합
        displayed_ids = {user.id for user in self.display_users}

        # 현재 표시된 모든 ID가 선택된 ID 집합에 포함되는지 확인
        return displayed_ids.issubset(self.selected_user_ids)

        # 일부만 선택되었으면 '중간 상태' 이거는 자바 스크립트에서 만 구현가능
        # return "indeterminate"

    # --- 폼의 특정 필드 값을 업데이트하는 이벤트 핸들러
    def set_form_field(self, field: str, value: str):
        """
        폼 데이터 딕셔너리의 특정 필드 값을 업데이트합니다.
        새 딕셔너리를 생성하여 할당함으로써 State 변경을 확실하게 감지시킵니다.
        """
        self.form_data = {
            **self.form_data,
            field: value,
        }

    # --- 전용 이벤트 핸들러 (on_change용) ---
    def set_role(self, selected_role: str):
        self.form_data = {**self.form_data, "role": selected_role}

    def set_department_id(self, selected_id: str):
        self.form_data = {**self.form_data, "department_id": selected_id}

        # 개별 사용자 선택/해제 토글
    def toggle_user_selection(self, user_id: int):
        """지정된 사용자 ID를 선택 목록에 추가하거나 제거합니다."""
        if user_id in self.selected_user_ids:
            self.selected_user_ids.remove(user_id)
        else:
            self.selected_user_ids.add(user_id)

    # 전체 선택/해제 토글
    def toggle_select_all(self):
        """현재 표시된 모든 사용자를 선택하거나 전체 선택을 해제합니다."""
        displayed_ids = {user.id for user in self.display_users}

        # 현재 표시된 항목들이 모두 선택된 상태가 아니면, 모두 선택
        if not displayed_ids.issubset(self.selected_user_ids):
            self.selected_user_ids.update(displayed_ids)
        else:
            # 모두 선택된 상태이면, 현재 표시된 항목들만 선택 해제
            self.selected_user_ids.difference_update(displayed_ids)

    # --- 이벤트 핸들러 ---
    # 페이지 로드 시 원본 부서 목록을 가져오는 함수
    def load_users_page(self):
        self.check_login()
        with rx.session() as session:
            statement = select(User).options(selectinload(User.department)).order_by(User.id)
            self.users = session.exec(statement).all()

            departments_from_db = session.exec(select(Department).order_by(Department.name)).all()
            self.department_options = [
                {"id": str(dept.id), "name": f"{dept.name} ({dept.code})"}
                for dept in departments_from_db
            ]

    def open_create_modal(self):
        self.is_edit = False
        self.form_data = {}
        self.show_modal = True

    def open_edit_modal(self, user_id: int):
        self.is_edit = True
        with rx.session() as session:
            user = session.get(User, user_id)
            if user:
                # 1. 모델 객체를 딕셔너리로 변환하는 더 깔끔한 방식입니다.
                form_data = user.model_dump()

                # 2. department는 객체이므로 제거 (department_id 사용)
                form_data.pop("department", None)

                # 3. 역할(Enum)을 Select 컴포넌트가 사용할 값(정수)으로 변환합니다.
                role_value = form_data.get("role")
                if isinstance(role_value, enum.Enum):
                    form_data["role"] = role_value.value

                # 4. 모든 값을 문자열로 변환하되, 'None'은 그대로 유지합니다.
                #    이것이 UniqueViolation 오류를 막는 핵심입니다.
                for key, value in form_data.items():
                    if value is not None:
                        form_data[key] = str(value)

                self.form_data = form_data
                self.show_modal = True
            else:
                return rx.window_alert("사용자를 찾을 수 없습니다.")

    def set_show_modal(self, open: bool):
        self.show_modal = open

    def handle_submit(self, form_data: dict):
        #  기존 form_data에 새로 받은 form_data를 병합합니다.
        self.form_data = {**self.form_data, **form_data}
        if self.is_edit:
            self.update_user()
        else:
            self.create_user()

    def create_user(self):
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

        self.close_and_reload()

    def update_user(self):
        user_id = int(self.form_data.get("id", 0))
        with rx.session() as session:
            user_to_update = session.get(User, user_id)
            if not user_to_update:
                return rx.window_alert("사용자를 찾을 수 없습니다.")

            update_data = self.form_data.copy()
            for key, value in update_data.items():
                if key in ["id", "login_id", "password", "created_at", "updated_at"]:
                    continue

                field_value = value
                if key == 'role' and value:
                    field_value = UserRole(int(value))
                elif key == 'department_id':
                    # 값이 있으면 정수형으로, 없으면 None으로
                    field_value = int(value) if value else None
                elif key == 'is_active':
                    field_value = str(value).lower() in ['true', '1']
                # code 필드가 빈 문자열이면 None으로 처리
                elif key == 'code' and not value:
                    field_value = None

                setattr(user_to_update, key, field_value)

            session.add(user_to_update)
            session.commit()

        self.close_and_reload()

    def delete_user(self, user_id: int):
        with rx.session() as session:
            user_to_delete = session.get(User, user_id)
            if not user_to_delete:
                return rx.window_alert("사용자를 찾을 수 없습니다.")
            if user_to_delete.role == UserRole.ADMIN:
                return rx.window_alert("관리자 계정은 삭제할 수 없습니다.")

            session.delete(user_to_delete)
            session.commit()
        self.load_users_page()

    def close_and_reload(self):
        self.show_modal = False
        self.form_data = {}
        self.load_users_page()


class DeptAdminState(BaseState):
    """부서 관리 페이지의 상태와 이벤트 핸들러"""
    departments: List[Department] = []
    show_modal: bool = False
    form_data: dict = {}
    is_edit: bool = False

    # 폼 필드 업데이트 핸들러
    def set_form_field(self, field: str, value: str):
        self.form_data = {**self.form_data, field: value}

    def load_depts_page(self):
        self.check_login()
        with rx.session() as session:
            self.departments = session.exec(select(Department).order_by(Department.name)).all()

    def open_create_modal(self):
        self.is_edit = False
        self.form_data = {}
        self.show_modal = True

    def open_edit_modal(self, department: Department):
        self.is_edit = True
        form_data = {}
        for field_name in department.__fields__:
            if field_name != "users":
                form_data[field_name] = getattr(department, field_name)
        self.form_data = form_data
        self.show_modal = True

    def set_show_modal(self, open: bool):
        self.show_modal = open

    def handle_submit(self, form_data: dict):
        #  기존 form_data에 새로 받은 form_data를 병합합니다.
        self.form_data = {**self.form_data, **form_data}
        if self.is_edit:
            self.update_department()
        else:
            self.create_department()

    def create_department(self):
        code = self.form_data.get("code")
        name = self.form_data.get("name")
        if not code or not name:
            return rx.window_alert("부서 코드와 이름은 필수입니다.")

        with rx.session() as session:
            if session.exec(select(Department).where(Department.code == code)).first():
                return rx.window_alert("이미 사용 중인 부서 코드입니다.")
            if session.exec(select(Department).where(Department.name == name)).first():
                return rx.window_alert("이미 사용 중인 부서 이름입니다.")

            new_dept = Department(
                code=code,
                name=name,
                notes=self.form_data.get("notes"),
            )
            session.add(new_dept)
            session.commit()

        self.close_and_reload()

    def update_department(self):
        dept_id = self.form_data.get("id")
        with rx.session() as session:
            dept_to_update = session.get(Department, dept_id)
            if not dept_to_update:
                return rx.window_alert("부서를 찾을 수 없습니다.")

            dept_to_update.name = self.form_data.get("name")
            dept_to_update.notes = self.form_data.get("notes")

            session.add(dept_to_update)
            session.commit()

        self.close_and_reload()

    def delete_department(self, dept_id: int):
        with rx.session() as session:
            user_count = session.exec(select(User).where(User.department_id == dept_id)).first()
            if user_count:
                return rx.window_alert("소속된 사용자가 있어 부서를 삭제할 수 없습니다.")

            dept_to_delete = session.get(Department, dept_id)
            if dept_to_delete:
                session.delete(dept_to_delete)
                session.commit()
        self.load_depts_page()

    def close_and_reload(self):
        self.show_modal = False
        self.form_data = {}
        self.load_depts_page()
