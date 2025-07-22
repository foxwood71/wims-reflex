from typing import Any 
import reflex as rx
from .state import UserAdminState, DeptAdminState


# =============================================================================
# 1. 사용자 관리 페이지 컴포넌트
# =============================================================================

def user_modal() -> rx.Component:
    """사용자 생성 및 수정을 위한 다이얼로그(팝업) 컴포넌트입니다."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.dialog.title(
                        rx.cond(UserAdminState.is_edit, "사용자 수정", "사용자 생성")
                    ),
                    rx.input(
                        name="login_id",
                        placeholder="로그인 ID (수정 불가)",
                        default_value=UserAdminState.form_data.get("login_id", ""),
                        is_disabled=UserAdminState.is_edit,
                        required=True,
                    ),
                    rx.input(
                        name="email",
                        placeholder="이메일",
                        type="email",
                        default_value=UserAdminState.form_data.get("email", ""),
                        required=True
                    ),
                    rx.input(
                        name="name",
                        placeholder="이름",
                        default_value=UserAdminState.form_data.get("name", "")
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="역할 선택"),
                        rx.select.content(
                            rx.foreach(
                                UserAdminState.role_options,
                                lambda role: rx.select.item(role["name"], value=role["id"])
                            )
                        ),
                        name="role",
                        value=UserAdminState.form_role_id,  # 계산된 속성 사용
                        on_change=UserAdminState.set_role,   # 전용 핸들러 사용
                        required=True,
                    ),

                    # 부서(Department) 선택 드롭다운
                    rx.select.root(
                        rx.select.trigger(placeholder="부서 선택"),
                        rx.select.content(
                            rx.foreach(
                                UserAdminState.department_options,
                                lambda dept: rx.select.item(dept["name"], value=dept["id"])
                            )
                        ),
                        name="department_id",
                        # value=UserAdminState.form_data.get("department_id", ""),
                        # on_change=lambda value: UserAdminState.set_form_field("department_id", value),
                        value=UserAdminState.form_department_id,  # 계산된 속성 사용
                        on_change=UserAdminState.set_department_id,   # 전용 핸들러 사용
                        required=True,
                    ),

                    rx.cond(
                        ~UserAdminState.is_edit,
                        rx.input(
                            name="password",
                            placeholder="비밀번호",
                            type="password",
                            required=True
                        ),
                    ),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("취소", type="button", color_scheme="gray")
                        ),
                        rx.button("저장", type="submit"),

                        justify="end",
                        spacing="3",
                        padding_top="1rem",
                        width="100%",   # hstack 자체의 너비를 100%로 설정
                    ),
                    align_items="stretch",
                    spacing="4",
                    width="100%",
                ),
                on_submit=UserAdminState.handle_submit,
                width="100%",
                # 🔽 이 속성을 추가하여 form이 남는 공간을 모두 채우도록 합니다.
                flex_grow="1",
            ),
            style={
                "max_width": "300px",
                "width": "100%",
            },
        ),
        open=UserAdminState.show_modal,
        on_open_change=UserAdminState.set_show_modal,
    )


def user_admin_page() -> rx.Component:
    """사용자 관리 페이지의 메인 컨텐츠입니다."""
    return rx.vstack(
        rx.hstack(
            rx.heading("사용자 목록", size="7"),
            rx.spacer(),
            rx.button("새 사용자 생성", on_click=UserAdminState.open_create_modal, size="3"),
            align="center",
            width="100%",
        ),
        # 검색 필터 섹션
        rx.hstack(
            rx.select.root(
                rx.select.trigger(placeholder="부서별로 필터링", width="140px"),
                rx.select.content(
                    # '전체' 옵션을 맨 위에 추가합니다.
                    #rx.select.item("전체 부서", value=""),
                    rx.foreach(
                        UserAdminState.filter_department_options,
                        lambda dept: rx.select.item(dept.name, value=dept.id)
                    ),
                ),
                # state의 필터 변수와 값을 바인딩합니다.
                #value=UserAdminState.filter_department_id,
                # 값이 변경되면 state를 업데이트하는 핸들러를 호출합니다.
                #on_change=UserAdminState.set_filter_department,
            ),
            rx.input(
                placeholder="ID, 이름, 이메일로 검색...",
                # 값이 변경되면 state를 업데이트하는 핸들러를 호출합니다.
                #on_change=UserAdminState.set_filter_search,
                # state의 필터 변수와 값을 바인딩합니다.
                #value=UserAdminState.filter_search_term,
                #flex_grow="0",  #  남은 공간을 모두 차지하도록 설정
            ),
            rx.spacer(),
            rx.button(rx.icon(tag="search"), "검색", on_click=UserAdminState.open_create_modal, size="2"),
            spacing="4",
            width="100%",
            padding_y="1rem",  # 위아래 여백 추가
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell(
                        rx.checkbox(
                            # 계산된 속성에 체크 상태를 바인딩
                            checked=UserAdminState.select_all_checked_state,
                            # 클릭 시 전체 선택/해제 핸들러 호출
                            on_change=UserAdminState.toggle_select_all,
                        )
                    ),
                    rx.table.column_header_cell("ID"),
                    rx.table.column_header_cell("로그인 ID"),
                    rx.table.column_header_cell("이름"),
                    rx.table.column_header_cell("이메일"),
                    rx.table.column_header_cell("역할"),
                    rx.table.column_header_cell("부서"),
                    rx.table.column_header_cell("상태"),
                    rx.table.column_header_cell("작업"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    UserAdminState.display_users,
                    lambda user: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                # 현재 사용자의 ID가 선택 목록(set)에 있는지 확인하여 체크 상태 결정
                                checked=UserAdminState.selected_user_ids.contains(user.id),
                                # 클릭 시 개별 선택 핸들러 호출
                                on_change=lambda: UserAdminState.toggle_user_selection(user.id),
                            )
                        ),
                        rx.table.cell(user.id),
                        rx.table.cell(user.login_id),
                        rx.table.cell(user.name),
                        rx.table.cell(user.email),
                        rx.table.cell(user.role_name),
                        rx.table.cell(user.department_name),
                        rx.table.cell(
                            rx.badge(
                                rx.cond(user.is_active, "활성", "비활성"),
                                color_scheme=rx.cond(user.is_active, "grass", "ruby")
                            )
                        ),
                        rx.table.cell(
                            rx.hstack(
                                rx.button("수정", on_click=lambda: UserAdminState.open_edit_modal(user["id"]), size="1"),
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
    """부서 생성 및 수정을 위한 다이얼로그 컴포넌트입니다."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.form(
                rx.vstack(
                    rx.dialog.title(
                        rx.cond(DeptAdminState.is_edit, "부서 수정", "부서 생성")
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
                        rx.dialog.close(
                            rx.button("취소", type="button", color_scheme="gray")
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
        ),
        open=DeptAdminState.show_modal,
        on_open_change=DeptAdminState.set_show_modal,
    )


def department_admin_page() -> rx.Component:
    """부서 관리 페이지의 메인 컨텐츠입니다."""
    return rx.vstack(
        rx.hstack(
            rx.heading("부서 목록", size="7"),
            rx.spacer(),
            rx.button("새 부서 생성", on_click=DeptAdminState.open_create_modal, size="3"),
            align="center",
            width="100%",
        ),
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
                                rx.button("수정", on_click=lambda: DeptAdminState.open_edit_modal(dept), size="1"),
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
        dept_modal(),
        spacing="5",
        width="100%",
        on_mount=DeptAdminState.load_depts_page,
    )
