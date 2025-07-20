# /wims_project/wims/components/layout.py
"""
모든 페이지를 감싸는 공통 레이아웃 컴포넌트(네비게이션 바, 사이드바)를 정의합니다.
"""
import reflex as rx
from ..state.base import BaseState, MenuItem, SubItem
from .. import styles


# =============================================================================
# 레이아웃을 구성하는 하위 컴포넌트들
# =============================================================================

def navbar() -> rx.Component:
    """상단 네비게이션 바 컴포넌트."""
    return rx.hstack(
        rx.hstack(
            rx.icon(
                tag="menu",
                on_click=BaseState.toggle_sidebar,
                cursor="pointer",
                size=24
            ),
            rx.text(
                "WIMS",
                font_size="1.5em",
                font_weight="bold",
                margin_left="15px"
            ),
            spacing="4"
        ),
        rx.spacer(),
        rx.hstack(
            rx.icon(tag="bell", font_size="1.5em"),
            rx.icon(tag="settings", font_size="1.5em"),
            rx.popover.root(
                rx.popover.trigger(
                    rx.avatar(fallback=BaseState.logged_in_user.login_id[0].upper(), size="2", radius="full", cursor="pointer")
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.text(BaseState.logged_in_user.name, font_weight="bold"),
                        rx.text(BaseState.logged_in_user.email, color_scheme="gray"),
                        rx.popover.close(
                            rx.button("로그아웃", on_click=BaseState.logout, width="100%", margin_top="0.5rem")
                        ),
                        spacing="3",
                        align="center",
                    ),
                    align="center",
                    side="bottom",
                )
            ),
            spacing="4",
            align="center",
        ),
        **styles.navbar_style()
    )


def submenu_item_component(sub_item: SubItem) -> rx.Component:
    """서브 메뉴 아이템 컴포넌트."""
    return rx.link(
        rx.button(
            rx.text(sub_item.text, width="100%", text_align="left"),
            **styles.submenu_item_style()
        ),
        href=sub_item.url,
        width="100%",
        _hover={"text_decoration": "none"},
    )


def sidebar_menu_item_component(menu_item: MenuItem) -> rx.Component:
    """사이드바의 메인 메뉴 아이템 컴포넌트."""
    is_expanded = BaseState.open_submenu == menu_item.name

    return rx.vstack(
        rx.hstack(
            rx.icon(tag=menu_item.icon, min_width="20px"),
            rx.text(
                menu_item.name,
                **styles.sidebar_text_style(BaseState.is_sidebar_open)
            ),
            rx.spacer(),
            rx.cond(
                (BaseState.is_sidebar_open) & (menu_item.sub_items),
                rx.icon(
                    tag=rx.cond(is_expanded, "chevron_down", "chevron_right"),
                    size=20,
                ),
            ),
            on_click=lambda: BaseState.handle_menu_click(menu_item),
            **styles.main_menu_button_style(),
            cursor="pointer",
        ),
        rx.cond(
            BaseState.is_sidebar_open & (menu_item.sub_items is not None),
            rx.vstack(
                # [수정] 아래의 foreach 부분을 lambda로 감싸줍니다.
                rx.foreach(
                    menu_item.sub_items,
                    lambda sub: submenu_item_component(sub)
                ),
                **styles.submenu_container_style(is_expanded),
                spacing="1",
            )
        ),
        width="100%",
        align_items="flex-start",
        spacing="0",
    )


def sidebar() -> rx.Component:
    return rx.vstack(
        rx.foreach(
            BaseState.filtered_menu,
            sidebar_menu_item_component
        ),
        rx.spacer(),
        **styles.sidebar_style(BaseState.is_sidebar_open),
    )


# =============================================================================
# 전체 페이지를 감싸는 메인 템플릿
# =============================================================================
def template(page_content: rx.Component) -> rx.Component:
    """
    모든 페이지를 감싸는 메인 템플릿.
    네비게이션 바와 사이드바를 포함합니다.
    """
    return rx.box(
        rx.cond(
            BaseState.is_hydrated & (BaseState.logged_in_user != None),
            rx.fragment(
                navbar(),
                sidebar(),
                rx.box(
                    page_content,
                    **styles.main_content_box_style(BaseState.is_sidebar_open),
                    margin_top=styles.HEADER_HEIGHT,
                ),
            )
        ),
        width="100%",
        background_color="var(--gray-1)",
    )