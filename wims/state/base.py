# /wims_project/wims/state/base.py
import reflex as rx
from typing import List, Optional, Dict
from sqlmodel import select
from ..domains.usr.models import User, UserRole  #  usr 도메인의 모델 사용
from ..utils import verify_password  #  유틸리티 함수 임포트 (아래에서 생성)


#  [신규] 메뉴 데이터 구조에 url 필드 추가 (페이지 이동용)
class SubItem(rx.Base):
    text: str
    url: str
    roles: List[UserRole]


class MenuItem(rx.Base):
    icon: str
    name: str
    url: Optional[str] = None
    roles: List[UserRole]
    sub_items: Optional[List[SubItem]]


class BaseState(rx.State):
    """
    모든 State가 상속하는 전역 상태.
    UI 레이아웃 및 인증 상태를 관리합니다.
    """
    #  --- 인증 상태 ---
    logged_in_user: Optional[User] = None

    #  --- UI 레이아웃 상태 ---
    is_sidebar_open: bool = True
    open_submenu: str = ""

    #  [수정] 메뉴 데이터를 새 구조에 맞게 정의하고, 역할 기반 접근 제어(RBAC)를 적용합니다.
    menu_data: List[Dict] = [
        {
            "icon": "house", "name": "홈", "url": "/dashboard",
            "roles": [UserRole.ADMIN, UserRole.GENERAL_USER],
        },
        {
            "icon": "users", "name": "사용자 관리", "roles": [UserRole.ADMIN],
            "sub_items": [
                {"text": "사용자 목록", "url": "/admin/users", "roles": [UserRole.ADMIN]},
                {"text": "부서 목록", "url": "/admin/departments", "roles": [UserRole.ADMIN]},
            ]
        },
        {
            "icon": "flask-conical", "name": "실험 관리 (LIMS)", "roles": [UserRole.ADMIN, UserRole.LAB_MANAGER, UserRole.LAB_ANALYST],
            "sub_items": [
                {"text": "실험 의뢰", "url": "/lims/requests", "roles": [UserRole.ADMIN, UserRole.LAB_MANAGER]},
                {"text": "분석 결과", "url": "/lims/results", "roles": [UserRole.ADMIN, UserRole.LAB_ANALYST]},
            ]
        },
        {
            "icon": "package-2", "name": "자재 관리 (INV)", "roles": [UserRole.ADMIN, UserRole.INVENTORY_MANAGER],
            "sub_items": [
                {"text": "자재 목록", "url": "/inv/materials", "roles": [UserRole.ADMIN, UserRole.INVENTORY_MANAGER]},
            ]
        },
    ]

    @rx.var
    def filtered_menu(self) -> List[MenuItem]:
        """로그인한 사용자의 역할에 따라 접근 가능한 메뉴만 필터링합니다."""
        if not self.logged_in_user:
            return []

        filtered = []
        for menu_dict in self.menu_data:
            #  [수정] Pydantic 모델을 사용하여 안전하게 데이터 파싱
            menu = MenuItem.parse_obj(menu_dict)
            if self.logged_in_user.role in menu.roles:
                if menu.sub_items:
                    menu.sub_items = [
                        sub for sub in menu.sub_items
                        if self.logged_in_user.role in sub.roles
                    ]
                filtered.append(menu)
        return filtered

    #  --- 인증 이벤트 핸들러 ---
    def login(self, form_data: dict):
        """사용자 로그인"""
        login_id = form_data.get("login_id")
        password = form_data.get("password")
        if not login_id or not password:
            return rx.window_alert("아이디와 비밀번호를 입력해주세요.")

        with rx.session() as session:
            user = session.exec(select(User).where(User.login_id == login_id)).one_or_none()
            if user and verify_password(password, user.password_hash):
                self.logged_in_user = user
                return rx.redirect("/dashboard")
            else:
                return rx.window_alert("아이디 또는 비밀번호가 잘못되었습니다.")

    def logout(self):
        """사용자 로그아웃"""
        self.reset()
        return rx.redirect("/")

    def check_login(self):
        """페이지 접근 시 로그인 여부 확인"""
        if not self.is_hydrated or self.logged_in_user is None:
            return rx.redirect("/")

    # --- UI 이벤트 핸들러 ---
    def toggle_sidebar(self):
        """사이드바 열기/닫기"""
        self.is_sidebar_open = not self.is_sidebar_open
        if not self.is_sidebar_open:
            self.open_submenu = ""

    def handle_menu_click(self, menu: MenuItem):
        """메뉴 클릭 시 서브메뉴를 토글하거나 페이지로 이동합니다."""
        if menu.sub_items:  #  서브메뉴가 있으면
            if not self.is_sidebar_open:
                self.is_sidebar_open = True
            self.open_submenu = "" if self.open_submenu == menu.name else menu.name
        elif menu.url:  #  서브메뉴 없고 URL이 있으면
            self.open_submenu = ""
            return rx.redirect(menu.url)