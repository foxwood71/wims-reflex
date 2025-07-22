import reflex as rx

config = rx.Config(
    app_name="wims",
    # db_url="postgresql+asyncpg://wims:wims1234@localhost:5432/wims_dbv1",  # 비동기 사용자 환경에 맞게 수정
    db_url="postgresql://wims:wims1234@localhost:5432/wims_dbv1",   # 동기
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
