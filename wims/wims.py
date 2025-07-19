import reflex as rx
from . import styles
from typing import List  #  List를 typing에서 import 합니다.


# --- 데이터 모델 정의 ---
class SubItem(rx.Base):
    text: str
    content: str
    roles: List[str]


class MenuItem(rx.Base):
    icon: str
    name: str
    roles: List[str]
    sub_items: List[SubItem]


# --- 상태 정의 (State) ---
class State(rx.State):
    """The app state."""
    current_main_content: str = "대시보드"
    is_sidebar_open: bool = False
    open_submenu: str = ""
    selected_main_menu: str = "홈"
    selected_sub_menu: str = ""
    user_role: str = "user"

    menu_data: list[MenuItem] = [
        {
            "icon": "factory", "name": "설비", "roles": ["admin", "user"],
            "sub_items": [
                {"text": "설비 목록", "content": "설비 목록 페이지", "roles": ["admin", "user"]},
                {"text": "설비 등록", "content": "설비 등록 페이지", "roles": ["admin"]},
                {"text": "설비 점검", "content": "설비 점검 페이지", "roles": ["admin", "user"]},
            ]
        },
        {
            "icon": "package_2", "name": "자재", "roles": ["admin", "user"],
            "sub_items": [
                {"text": "자재 목록", "content": "자재 목록 페이지", "roles": ["admin", "user"]},
                {"text": "자재 입고", "content": "자재 입고 페이지", "roles": ["admin"]},
                {"text": "자재 출고", "content": "자재 출고 페이지", "roles": ["admin"]},
            ]
        },
        {
            "icon": "square-activity", "name": "운영", "roles": ["admin", "user"],
            "sub_items": [
                {"text": "운영 대시보드", "content": "운영 대시보드", "roles": ["admin", "user"]},
                {"text": "생산 계획", "content": "생산 계획 페이지", "roles": ["admin"]},
            ]
        },
        {
            "icon": "flask-conical", "name": "실험", "roles": ["admin", "user"],
            "sub_items": [
                {"text": "실험 의뢰", "content": "실험 관리 페이지", "roles": ["admin", "user"]},
                {"text": "분석 결과", "content": "데이터 분석 페이지", "roles": ["admin"]},
                {"text": "데이터 검증", "content": "데이터 검증 페이지", "roles": ["admin"]},
            ]
        },
        {
            "icon": "users", "name": "사용자", "roles": ["admin"],
            "sub_items": [
                {"text": "사용자 목록", "content": "사용자 목록", "roles": ["admin"]},
            ]
        },
        {
            "icon": "info", "name": "공지사항", "roles": ["admin", "user", "guest"],
            "sub_items": [
                {"text": "최신 공지", "content": "최신 공지 페이지", "roles": ["admin", "user", "guest"]},
            ]
        },
        
    ]

    @rx.var
    # 반환 타입을 list[dict]에서 list[MenuItem]으로 변경
    def filtered_menu_data(self) -> list[MenuItem]:
        """사용자 역할에 따라 필터링된 메뉴 데이터를 반환합니다."""
        # Reflex가 자동으로 menu_data의 각 항목을 MenuItem 객체처럼 다룹니다.
        return [
            MenuItem(**menu) for menu in self.menu_data
            if self.user_role in menu['roles']
        ]

    def open_sidebar(self):
        self.is_sidebar_open = True

    def close_sidebar(self):
        self.is_sidebar_open = False
        self.open_submenu = ""

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open
        if not self.is_sidebar_open:
            self.open_submenu = ""

    def toggle_submenu(self, menu_name: str):
        if self.open_submenu == menu_name:
            self.open_submenu = ""
        else:
            self.open_submenu = menu_name
            self.is_sidebar_open = True

    def set_selected_main_menu(self, menu_name: str):
        self.selected_main_menu = menu_name
        self.selected_sub_menu = ""
        self.current_main_content = f"{menu_name} 대시보드"

    def handle_main_menu_click(self, menu_name: str):
        """메인 메뉴 클릭 시 서브메뉴 토글 및 선택된 메뉴 설정을 한 번에 처리합니다."""
        self.toggle_submenu(menu_name)
        self.set_selected_main_menu(menu_name)

    def set_selected_sub_menu(self, main_menu_name: str, sub_menu_text: str, content_name: str):
        self.selected_main_menu = main_menu_name
        self.selected_sub_menu = sub_menu_text
        self.current_main_content = content_name

    def set_user_role(self, role: str):
        self.user_role = role
        self.current_main_content = "대시보드"
        self.selected_main_menu = "홈"
        self.selected_sub_menu = ""
        self.open_submenu = ""


# --- 컴포넌트 (Components) ---
def navbar():
    """상단 네비게이션 바 컴포넌트."""
    return rx.hstack(
        rx.hstack(
            rx.icon(tag="menu", on_click=State.toggle_sidebar, cursor="pointer", size=24),
            rx.text("LIMS WEB", font_size="1.5em", font_weight="bold", margin_left="15px"),
            spacing="4"
        ),
        rx.hstack(
            rx.text(State.selected_main_menu, color="gray", font_weight="bold"),
            rx.cond(
                State.selected_sub_menu != "",
                rx.hstack(
                    rx.text(" > ", color="gray"),
                    rx.text(State.selected_sub_menu, color="gray", font_weight="bold"),
                )
            )
        ),
        rx.spacer(),
        rx.select(
            ["admin", "user", "guest"],
            value=State.user_role,
            on_change=State.set_user_role,
            size="2",
            margin_right="10px",
        ),
        rx.hstack(
            rx.icon(tag="bell", font_size="1.5em", margin_left="10px"),
            rx.icon(tag="settings", font_size="1.5em", margin_left="10px"),
            rx.icon(tag="user", font_size="1.5em", margin_left="10px"),
        ),
        **styles.navbar_style()
    )


def submenu_item_component(main_menu_name: str, sub_item: SubItem):
    """서브 메뉴 아이템 컴포넌트."""
    return rx.cond(
        sub_item.roles.contains(State.user_role),
        rx.button(
            rx.text(sub_item.text, width="100%", text_align="left"),
            on_click=lambda: State.set_selected_sub_menu(
                main_menu_name, sub_item.text, sub_item.content
            ),
            **styles.submenu_item_style()
        )
    )


def sidebar_menu_item_component(menu_item: MenuItem):
    """메인 사이드바 메뉴 아이템 컴포넌트."""
    is_expanded = State.open_submenu == menu_item.name
    
    # 클릭 가능한 영역을 rx.button 대신 rx.hstack으로 만듭니다.
    return rx.vstack(
        rx.hstack(
            # 왼쪽 아이콘과 텍스트
            rx.hstack(
                rx.icon(tag=menu_item.icon, min_width="20px"),
                rx.text(
                    menu_item.name,
                    **styles.sidebar_text_style(State.is_sidebar_open)
                ),
                spacing="4",
            ),
            # 오른쪽 펼침 아이콘
            rx.cond(
                # 서브메뉴가 있을 때만 아이콘을 표시하도록 조건을 강화합니다.
                (State.is_sidebar_open) & (menu_item.sub_items),
                rx.icon(
                    tag=rx.cond(is_expanded, "chevron_down", "chevron_right"),
                    size=20,
                    position="absolute",
                    right="2px",
                    top="50%",
                    transform="translateY(-50%)",
                    # ✅ z_index를 추가하여 아이콘이 항상 위에 표시되도록 합니다.
                    z_index="2",
                ),
            ),
            # hstack에 직접 이벤트와 스타일을 적용합니다.
            on_click=State.handle_main_menu_click(menu_item.name),
            **styles.main_menu_button_style(),
            _hover={"background_color": "rgba(0, 0, 0, 0.05)"},
            cursor="pointer",
        ),
        # 서브메뉴 부분은 동일합니다.
        rx.cond(
            State.is_sidebar_open,
            rx.vstack(
                rx.foreach(
                    menu_item.sub_items,
                    lambda sub: submenu_item_component(menu_item.name, sub)
                ),
                **styles.submenu_container_style(is_expanded),
                spacing="1",
            )
        ),
        width="100%",
        align_items="flex-start",
        spacing="0",
    )


def sidebar():
    """좌측 사이드바 컴포넌트."""
    return rx.vstack(
        rx.foreach(
            State.filtered_menu_data,
            sidebar_menu_item_component
        ),
        rx.spacer(),
        **styles.sidebar_style(State.is_sidebar_open),
    )


def dashboard_content():
    """대시보드 내용 컴포넌트."""
    return rx.vstack(
        rx.heading(State.current_main_content, size="7"),
        rx.text(f"현재 사용자 역할: {State.user_role}"),
        rx.text("여기에 대시보드 컨텐츠를 추가하세요."),
        spacing="4",
        align="center",
        justify="center",
        width="100%",
        height="100%",
    )


def index():
    """메인 페이지 (고정 레이아웃 적용)."""
    return rx.box(
        navbar(),
        sidebar(),
        rx.box(
            dashboard_content(),
            **styles.main_content_box_style(State.is_sidebar_open),
            margin_top=styles.HEADER_HEIGHT,
        ),
        width="100%",
        background_color="#fafafa",
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="jade",
        gray_color="slate",
        radius="medium",
    ),
    style={"font_size": "16px"}
)

app.add_page(index, "/")