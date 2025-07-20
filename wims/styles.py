# /wims_project/wims/styles.py
"""
애플리케이션 전반에 사용될 UI 컴포넌트들의 스타일을 정의하는 모듈입니다.
CSS 속성을 딕셔너리 형태로 반환하는 함수들을 포함합니다.
"""

import reflex as rx

#  --- 전역 스타일 상수 ---
HEADER_HEIGHT = "60px"
SIDEBAR_CLOSED_WIDTH = "60px"
SIDEBAR_OPEN_WIDTH = "220px"  #  너비를 약간 조정하여 텍스트 잘림 방지

#  --- 공통 애니메이션 효과 ---
TRANSITION_EFFECT = "width 0.3s ease-in-out, margin-left 0.3s ease-in-out"
OPACITY_TRANSITION_EFFECT = "opacity 0.2s ease-in-out"
MENU_EXPAND_TRANSITION = "max-height 0.3s ease-out, opacity 0.3s ease-out"

#  --- 색상 팔레트 ---
SUBMENU_BG_COLOR = "var(--gray-2)"
SUBMENU_TEXT_COLOR = "var(--gray-11)"


#  --- 컴포넌트별 스타일 함수 ---

def navbar_style() -> dict:
    """상단 네비게이션 바 스타일"""
    return {
        "width": "100%",
        "height": HEADER_HEIGHT,
        "padding": "0 20px",
        "border_bottom": "1px solid var(--gray-4)",
        "align_items": "center",
        "position": "fixed",
        "top": "0",
        "z_index": "1000",
        "background_color": "white",
    }


def sidebar_style(is_open: rx.Var[bool]) -> dict:
    """좌측 사이드바 스타일"""
    return {
        "width": rx.cond(is_open, SIDEBAR_OPEN_WIDTH, SIDEBAR_CLOSED_WIDTH),
        "height": f"calc(100vh - {HEADER_HEIGHT})",
        "padding": "1rem 0.5rem",
        "border_right": "1px solid var(--gray-4)",
        "align_items": "flex-start",
        "transition": TRANSITION_EFFECT,
        "position": "fixed",
        "left": "0",
        "top": HEADER_HEIGHT,
        "z_index": "900",
        "background_color": "white",
        "overflow_x": "hidden",
        "overflow_y": "auto",
    }


def sidebar_text_style(is_open: rx.Var[bool]) -> dict:
    """사이드바 메뉴 아이템 텍스트 스타일"""
    return {
        "opacity": rx.cond(is_open, "1", "0"),
        "transition": OPACITY_TRANSITION_EFFECT,
        "pointer_events": rx.cond(is_open, "auto", "none"),
        "white_space": "nowrap",
        "overflow": "hidden",
        "text_overflow": "ellipsis",
    }


def main_content_box_style(is_sidebar_open: rx.Var[bool]) -> dict:
    """메인 컨텐츠 영역 스타일"""
    return {
        "width": rx.cond(
            is_sidebar_open,
            f"calc(100% - {SIDEBAR_OPEN_WIDTH})",
            f"calc(100% - {SIDEBAR_CLOSED_WIDTH})"
        ),
        "height": f"calc(100vh - {HEADER_HEIGHT})",
        "padding": "2rem",
        "margin_left": rx.cond(is_sidebar_open, SIDEBAR_OPEN_WIDTH, SIDEBAR_CLOSED_WIDTH),
        "transition": TRANSITION_EFFECT,
        "overflow_y": "auto",
        "z_index": "1",
    }


def submenu_container_style(is_expanded: rx.Var[bool]) -> dict:
    """서브 메뉴 컨테이너 스타일"""
    return {
        "width": "100%",
        "overflow": "hidden",
        "max_height": rx.cond(is_expanded, "200px", "0px"),
        "opacity": rx.cond(is_expanded, "1", "0"),
        "transition": MENU_EXPAND_TRANSITION,
        "padding_left": "2.2rem",  #  아이콘 너비만큼 들여쓰기
        "box_sizing": "border-box",
        "background_color": SUBMENU_BG_COLOR,
        "border_radius": "var(--radius-2)",
    }


def submenu_item_style() -> dict:
    """서브 메뉴 아이템 스타일"""
    return {
        "width": "100%",
        "justify_content": "flex-start",
        "variant": "ghost",
        "size": "2",
        "margin_y": "1px",
        "color": SUBMENU_TEXT_COLOR,
        "padding_left": "0.5rem",
        "_hover": {
            "background_color": "var(--accent-3)"
        }
    }


def main_menu_button_style() -> dict:
    """사이드바 주메뉴 아이템 스타일"""
    return {
        "width": "100%",
        "justify_content": "flex-start",
        "padding": "0.5rem 0.8rem",
        "variant": "ghost",
        "size": "3",
        "margin_y": "4px",
        "overflow": "hidden",
        "position": "relative",
        "_hover": {
            "background_color": "var(--gray-3)"
        }
    }