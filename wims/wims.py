# /wims_project/wims/wims.py
import reflex as rx
from .components.layout import template
from .pages.index import login_page
from .domains.usr.pages import user_admin_page, department_admin_page
# from .domains.lims.pages import ... # 향후 추가될 도메인 페이지

#  [신규] 간단한 대시보드 페이지 정의
def dashboard() -> rx.Component:
    return rx.heading("대시보드에 오신 것을 환영합니다.", size="7")

#  App 인스턴스 생성
app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="jade",
        gray_color="slate",
        radius="medium",
    ),
    style={"font_size": "16px"}
)

#  페이지 추가
#  로그인 페이지는 템플릿 없이 추가
app.add_page(login_page, route="/")

#  템플릿을 사용하는 페이지들
app.add_page(template(page_content=dashboard()), route="/dashboard")
app.add_page(template(page_content=user_admin_page()), route="/admin/users")
app.add_page(template(page_content=department_admin_page()), route="/admin/departments")

#  향후 추가될 LIMS 페이지 예시
# app.add_page(template(page_content=lims_requests_page()), route="/lims/requests")