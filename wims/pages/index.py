# /wims_project/wims/pages/index.py
"""
애플리케이션의 진입점 역할을 하는 로그인 페이지를 정의합니다.
이 페이지는 공통 레이아웃(template)을 사용하지 않습니다.
"""

import reflex as rx
from ..state.base import BaseState


def login_page() -> rx.Component:
    """
    사용자가 아이디와 비밀번호를 입력하여 로그인하는 UI 컴포넌트입니다.
    화면 중앙에 로그인 카드 형태로 표시됩니다.
    """
    return rx.flex(
        rx.card(
            rx.vstack(
                rx.heading("WIMS 로그인", size="7", align="center"),
                rx.text(
                    "시스템을 사용하려면 로그인하세요.",
                    align="center",
                    color_scheme="gray",
                    padding_bottom="1rem"
                ),
                #  로그인 폼: 제출 시 BaseState.login 이벤트 핸들러를 호출합니다.
                rx.form(
                    rx.vstack(
                        rx.input(
                            name="login_id",
                            placeholder="로그인 ID",
                            required=True,
                            size="3"
                        ),
                        rx.input(
                            name="password",
                            placeholder="비밀번호",
                            type="password",
                            required=True,
                            size="3"
                        ),
                        rx.button(
                            "로그인",
                            type="submit",
                            width="100%",
                            size="3",
                            margin_top="0.5rem"
                        ),
                        spacing="4",
                    ),
                    on_submit=BaseState.login,
                    width="100%",
                ),
                spacing="5",
            ),
            size="4",
            style={"min_width": "400px"}
        ),
        #  Flexbox를 사용하여 페이지 중앙에 배치
        align="center",
        justify="center",
        height="100vh",
        background="radial-gradient(circle, #f0f4f8, #d9e2ec)",
    )