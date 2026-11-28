from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import Session  # thêm ở đầu file
from app.db import engine  # thêm ở đầu file
from app.models import Product  # thêm ở đầu file
from sqlmodel import select  # thêm vào dòng import sqlmodel ở đầu file
from app.models import User  # thêm User vào dòng import models
from app.seed import seed_admin  # thêm ở đầu file

client = TestClient(app)

PEN = {"name": "Pen", "price": "1.10", "stock": 5}


def test_no_token_is_401():
    r = client.post("/products", json=PEN)

    assert r.status_code == 401


def test_customer_is_403(
    customer_headers,
):  # pytest chạy customer_headers() trước → được dict header
    r = client.post("/products", json=PEN, headers=customer_headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Admins only"}


def test_admin_creates_product(admin_headers):
    r = client.post("/products", json=PEN, headers=admin_headers)
    assert r.status_code == 201
    new_id = r.json()["id"]  # API trả sản phẩm vừa tạo, kèm id do PostgreSQL sinh

    with Session(
        engine
    ) as session:  # tự mở session, vì đây là test chứ không phải route
        saved = session.get(Product, new_id)  # đọc THẲNG từ DB, không qua API
    assert saved.name == "Pen"  # chứng minh đã lưu thật (AC1: "có trong PostgreSQL")


def test_seed_admin_twice_creates_one_admin():
    seed_admin()
    seed_admin()  # lần 2: seed_admin thấy email đã có → không tạo
    with Session(engine) as session:
        admins = session.exec(
            select(User).where(User.role == "admin")
        ).all()  # lấy MỌI admin
    assert len(admins) == 1  # chỉ 1, không trùng
    assert admins[0].hashed_password.startswith(
        "$argon2"
    )  # mật khẩu đã băm, không lưu chữ thô
