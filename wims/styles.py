import reflex as rx

# 전역 스타일 상수
MAX_WIDTH = "1200px"
HEADER_HEIGHT = "60px"
SIDEBAR_CLOSED_WIDTH = "60px"
SIDEBAR_OPEN_WIDTH = "200px"

# 공통 transition 효과
TRANSITION_EFFECT = "width 0.3s ease-in-out, margin-left 0.3s ease-in-out"
OPACITY_TRANSITION_EFFECT = "opacity 0.2s ease-in-out"
MENU_EXPAND_TRANSITION = "max-height 0.3s ease-out, opacity 0.3s ease-out"

# 색상 팔레트
SUBMENU_BG_COLOR = "#f5f5f5"
SUBMENU_TEXT_COLOR = "#555"


# Navbar 스타일
def navbar_style():
    return {
        "width": "100%",
        "height": HEADER_HEIGHT,
        "padding": "0 20px",
        "border_bottom": "1px solid #eee",
        "align_items": "center",
        "position": "fixed",
        "top": "0",
        "z_index": "1000",
        "background_color": "white",
    }


# Sidebar 스타일
def sidebar_style(is_open: bool):
    return {
        "width": rx.cond(is_open, SIDEBAR_OPEN_WIDTH, SIDEBAR_CLOSED_WIDTH),
        "height": f"calc(100vh - {HEADER_HEIGHT})",
        "padding_top": "20px",
        "border_right": "1px solid #eee",
        "align_items": "flex-start",
        "transition": TRANSITION_EFFECT,
        "position": "fixed",
        "left": "0",
        "top": HEADER_HEIGHT,
        "z_index": "900",
        "background_color": "white",
        "overflow_x": "hidden", # 사이드바가 닫혔을 때 내용 숨기기
        "overflow_y": "auto",
    }


# Sidebar 메뉴 아이템 텍스트 스타일
def sidebar_text_style(is_open: bool):
    return {
        "opacity": rx.cond(is_open, "1", "0"),
        "transition": OPACITY_TRANSITION_EFFECT,
        "pointer_events": rx.cond(is_open, "auto", "none"),
        "white_space": "nowrap",
        "overflow": "hidden",
        "text_overflow": "ellipsis",
    }


# Main Content Box 스타일
def main_content_box_style(is_sidebar_open: bool):
    return {
        "width": rx.cond(is_sidebar_open, f"calc(100% - {SIDEBAR_OPEN_WIDTH})", f"calc(100% - {SIDEBAR_CLOSED_WIDTH})"),
        "height": f"calc(100vh - {HEADER_HEIGHT})",
        "padding": "20px",
        "margin_left": rx.cond(is_sidebar_open, SIDEBAR_OPEN_WIDTH, SIDEBAR_CLOSED_WIDTH),
        "transition": TRANSITION_EFFECT,
        "overflow_y": "auto", # 콘텐츠가 길어지면 스크롤 생성
        "z_index": "1",
    }


# 대시보드 내용 스타일
def dashboard_content_style():
    return {
        "width": "100%",
        "height": "100%",
    }


# 서브 메뉴 컨테이너 스타일
def submenu_container_style(is_expanded: bool):
    return {
        "width": "100%",
        "overflow": "hidden",
        "max_height": rx.cond(is_expanded, "200px", "0px"),
        "opacity": rx.cond(is_expanded, "1", "0"),
        "transition": MENU_EXPAND_TRANSITION,
        "padding_left": "30px",
        "box_sizing": "border-box",
        "background_color": SUBMENU_BG_COLOR,
    }


# 서브 메뉴 아이템 스타일
def submenu_item_style():
    return {
        "width": "100%",
        "justify_content": "flex-start",
        "variant": "ghost",
        "size": "2",
        "margin_y": "1px",
        "color": SUBMENU_TEXT_COLOR,
        "padding_left": "0px",
        "_hover": {
            "background_color": "rgba(0, 0, 0, 0.05)"
        }
    }


def main_menu_button_style():
    """사이드바 버튼 (주메뉴) 스타일"""
    return {
        "width": "100%",
        "justify_content": "flex-start",
        "padding_left": "20px",
        "variant": "ghost",
        "size": "3",
        "margin_y": "4px",
        "overflow": "visible",
        # ✅ 아이콘 위치를 조절하기 위한 기준점으로 설정합니다.
        "position": "relative",
    }
