# /wims_project/wims/domains/usr/pages.py
"""
'usr' 도메인(사용자 및 부서 관리)의 UI 페이지 컨텐츠를 정의하는 모듈입니다.
"""

import reflex as rx
from .state import UserAdminState, DeptAdminState
from .models import UserRole


# =============================================================================
# 1. 사용자 관리 페이지 컴포넌트
# =============================================================================


def user_modal() -> rx.Component:
    """A dialog to create or edit a user."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.dialog.title(
                        rx.cond(UserAdminState.is_edit, "Edit User", "Create User")
                    ),
                    rx.input(
                        name="login_id",
                        placeholder="Login ID (cannot be changed)",
                        default_value=UserAdminState.form_data.get("login_id", ""),
                        is_disabled=UserAdminState.is_edit,
                        required=True,
                    ),
                    rx.input(
                        name="email",
                        placeholder="Email",
                        type="email",
                        default_value=UserAdminState.form_data.get("email", ""),
                        required=True
                    ),
                    rx.input(
                        name="name",
                        placeholder="Name",
                        default_value=UserAdminState.form_data.get("name", "")
                    ),

                    # Role selection dropdown
                    rx.select.root(
                        rx.select.trigger(placeholder="Select a Role"),
                        rx.select.content(
                            # [FIX] Access dictionary keys instead of attributes
                            rx.foreach(
                                UserAdminState.role_options,
                                lambda role: rx.select.item(role["label"], value=role["value"])
                            )
                        ),
                        name="role",
                        default_value=str(UserAdminState.form_data.get("role", "")),
                        required=True,
                    ),

                    # Department selection dropdown
                    rx.select.root(
                        rx.select.trigger(placeholder="Select a Department"),
                        rx.select.content(
                            rx.foreach(
                                UserAdminState.departments,
                                # [FIX] Changed rx.select.option to rx.select.item
                                lambda dept: rx.select.item(f"{dept.name} ({dept.code})", value=str(dept.id))
                            )
                        ),
                        name="department_id",
                        default_value=UserAdminState.form_data.get("department_id", ""),
                    ),
                    
                    rx.cond(
                        ~UserAdminState.is_edit,
                        rx.input(
                            name="password",
                            placeholder="Password",
                            type="password",
                            required=True
                        ),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cancel", type="button", color_scheme="gray")
                        ),
                        rx.button("Save", type="submit"),
                        spacing="3",
                        justify="end",
                        padding_top="1rem",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=UserAdminState.handle_submit,
            ),
        ),
        open=UserAdminState.show_modal,
        on_open_change=UserAdminState.set_show_modal,
    )

def user_admin_page() -> rx.Component:
    """사용자 관리 페이지의 메인 컨텐츠입니다."""
    return rx.vstack(
        # ... (페이지 헤더 부분은 동일) ...
        rx.hstack(
            rx.heading("사용자 목록", size="7"),
            rx.spacer(),
            rx.button("새 사용자 생성", on_click=UserAdminState.open_create_modal, size="3"),
            align="center",
            width="100%",
        ),
        rx.table.root(
            rx.table.header(
                # ... (테이블 헤더는 동일) ...
            ),
            rx.table.body(
                # [수정] UserAdminState.users 대신 display_users를 순회합니다.
                rx.foreach(
                    UserAdminState.display_users,
                    lambda user: rx.table.row(
                        # [수정] 모든 속성을 딕셔너리 키로 접근합니다.
                        rx.table.cell(user["id"]),
                        rx.table.cell(user["login_id"]),
                        rx.table.cell(user["name"]),
                        rx.table.cell(user["email"]),
                        rx.table.cell(user["role_name"]),
                        rx.table.cell(user["department_name"]),
                        rx.table.cell(
                            # [수정] python의 if/else 대신 rx.cond 사용
                            rx.badge(
                                rx.cond(user["is_active"], "활성", "비활성"),
                                color_scheme=rx.cond(user["is_active"], "grass", "ruby")
                            )
                        ),
                        rx.table.cell(
                            rx.hstack(
                                # [수정] 이벤트 핸들러에 user 객체 대신 user["id"]를 전달합니다.
                                rx.button(
                                    "수정",
                                    on_click=lambda: UserAdminState.open_edit_modal(user["id"]),
                                    size="1"
                                ),
                                rx.alert_dialog.root(
                                    rx.alert_dialog.trigger(
                                        rx.button("삭제", color_scheme="ruby", size="1")
                                    ),
                                    rx.alert_dialog.content(
                                        rx.alert_dialog.title("삭제 확인"),
                                        rx.alert_dialog.description(
                                            f"'{user['login_id']}' 사용자를 정말 삭제하시겠습니까?"
                                        ),
                                        rx.flex(
                                            rx.alert_dialog.cancel(
                                                rx.button("취소", color_scheme="gray")
                                            ),
                                            rx.alert_dialog.action(
                                                rx.button("삭제", on_click=lambda: UserAdminState.delete_user(user["id"]))
                                            ),
                                            spacing="3",
                                            justify="end",
                                            padding_top="1rem",
                                        ),
                                    ),
                                ),
                                spacing="2",
                            )
                        ),
                    )
                )
            ),
            variant="surface",
            width="100%",
        ),
        user_modal(),
        spacing="5",
        width="100%",
        on_mount=UserAdminState.load_users_page,
    )


# =============================================================================
# 2. 부서 관리 페이지 컴포넌트
# =============================================================================

def dept_modal() -> rx.Component:
    """부서 생성 및 수정을 위한 모달 컴포넌트입니다."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.heading(
                        rx.cond(DeptAdminState.is_edit, "부서 수정", "부서 생성"),
                        size="5"
                    ),
                    rx.input(
                        name="code",
                        placeholder="부서 코드 (예: HR, LAB)",
                        default_value=DeptAdminState.form_data.get("code", ""),
                        is_disabled=DeptAdminState.is_edit,
                        required=True
                    ),
                    rx.input(
                        name="name",
                        placeholder="부서 이름",
                        default_value=DeptAdminState.form_data.get("name", ""),
                        required=True
                    ),
                    rx.text_area(
                        name="notes",
                        placeholder="비고",
                        default_value=DeptAdminState.form_data.get("notes", "")
                    ),
                    rx.hstack(
                        rx.button(
                            "취소",
                            on_click=lambda: DeptAdminState.close_and_reload("load_depts_page"),
                            type="button",
                            color_scheme="gray"
                        ),
                        rx.button("저장", type="submit"),
                        justify="end",
                        spacing="3",
                        padding_top="1rem",
                    ),
                    spacing="4",
                ),
                on_submit=DeptAdminState.handle_submit,
            ),
            is_open=DeptAdminState.show_modal,
        )
    )


def department_admin_page() -> rx.Component:
    """부서 관리 페이지의 메인 컨텐츠입니다."""
    return rx.vstack(
        #  페이지 헤더
        rx.hstack(
            rx.heading("부서 목록", size="7"),
            rx.spacer(),
            rx.button("새 부서 생성", on_click=DeptAdminState.open_create_modal, size="3"),
            align="center",
            width="100%",
        ),
        #  부서 목록 테이블
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("ID"),
                    rx.table.column_header_cell("부서 코드"),
                    rx.table.column_header_cell("부서명"),
                    rx.table.column_header_cell("비고"),
                    rx.table.column_header_cell("작업"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    DeptAdminState.departments,
                    lambda dept: rx.table.row(
                        rx.table.cell(dept.id),
                        rx.table.cell(dept.code),
                        rx.table.cell(dept.name),
                        rx.table.cell(dept.notes),
                        rx.table.cell(
                            rx.hstack(
                                rx.button(
                                    "수정",
                                    on_click=lambda: DeptAdminState.open_edit_modal(dept),
                                    size="1"
                                ),
                                rx.alert_dialog.root(
                                    rx.alert_dialog.trigger(
                                        rx.button("삭제", color_scheme="ruby", size="1")
                                    ),
                                    rx.alert_dialog.content(
                                        rx.alert_dialog.title("삭제 확인"),
                                        rx.alert_dialog.description(
                                            f"'{dept.name}' 부서를 정말 삭제하시겠습니까?"
                                        ),
                                        rx.flex(
                                            rx.alert_dialog.cancel(
                                                rx.button("취소", color_scheme="gray")
                                            ),
                                            rx.alert_dialog.action(
                                                rx.button("삭제", on_click=lambda: DeptAdminState.delete_department(dept.id))
                                            ),
                                            spacing="3",
                                            justify="end",
                                            padding_top="1rem",
                                        ),
                                    ),
                                ),
                                spacing="2",
                            )
                        ),
                    )
                )
            ),
            variant="surface",
            width="100%",
        ),
        dept_modal(),  #  페이지에 모달 컴포넌트 포함
        spacing="5",
        width="100%",
        on_mount=DeptAdminState.load_depts_page,  #  페이지가 마운트될 때 데이터 로드
    )
