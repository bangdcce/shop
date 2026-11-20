# Kiến trúc dự án Shop: chọn gì, vì sao, bản chất ra sao

Người viết: Tech Lead · 20/11/2026 · Cập nhật khi kiến trúc thay đổi (và ghi 1 dòng vào [decisions.md](decisions.md)).

## 1. Chọn gì (tóm tắt 3 dòng)
1. **Một repo chứa cả backend và frontend (monorepo nhỏ):** `backend/`, `frontend/` (Sprint 2), `docs/`.
2. **Backend chia theo tầng (layered architecture):** tầng HTTP (`routes/`) → tầng nghiệp vụ (`services.py`) → tầng dữ liệu (`models.py` + `db.py` + PostgreSQL).
3. **Quy tắc phụ thuộc một chiều:** tầng trên được gọi tầng dưới, tầng dưới **không bao giờ** biết tầng trên.

## 2. Cây thư mục cuối Sprint 1
```
shop/
├── README.md              chạy thế nào, test thế nào (trang đầu tiên người khác đọc)
├── docs/                  quyết định và tài liệu của team (file này)
└── backend/
    ├── pyproject.toml     thư viện dự án cần;  uv.lock = phiên bản chính xác của từng thư viện
    ├── .env.example       danh sách biến môi trường (giá trị giả);  .env thật thì KHÔNG commit
    ├── alembic.ini, migrations/versions/   lịch sử thay đổi cấu trúc database (SHOP-003)
    ├── app/
    │   ├── main.py        tạo app, gắn các router            ← điểm vào
    │   ├── config.py      đọc cấu hình từ môi trường         ┐
    │   ├── db.py          kết nối PostgreSQL, session         ├ hạ tầng dùng chung
    │   ├── security.py    băm mật khẩu, JWT, phân quyền       ┘
    │   ├── models.py      bảng database + khuôn vào/ra API    ← dữ liệu
    │   ├── services.py    luật nghiệp vụ (khi luật đủ nhiều)  ← nghiệp vụ
    │   ├── seed.py        dữ liệu mẫu / admin đầu tiên
    │   └── routes/        HTTP: mỗi khu vực một file          ← cửa vào
    │       ├── products.py
    │       └── auth.py
    └── tests/
        ├── conftest.py    chuẩn bị chung: database test, đăng nhập sẵn
        ├── test_health.py
        ├── test_products.py
        └── test_auth.py
```

## 3. Bản chất: một request đi qua các tầng thế nào
Ví dụ: admin gọi `POST /products`.
```
HTTP request (chữ)
   │  uvicorn đọc byte → FastAPI chọn hàm theo URL
   ▼
routes/products.py   TẦNG HTTP: đọc body (Pydantic kiểm luật → 422), ai đang gọi (security.py → 401/403),
   │                 chọn mã trả về (201, 404...). KHÔNG chứa luật kinh doanh.
   ▼
services.py          TẦNG NGHIỆP VỤ: "được làm không, làm thế nào" (lọc, tính tiền, đặt hàng).
   │                 KHÔNG biết gì về HTTP: không có status code, không có request.
   ▼
models.py + db.py    TẦNG DỮ LIỆU: bảng, session, câu truy vấn → PostgreSQL.
```
Mỗi tầng chỉ có **một lý do để thay đổi**:
| Chuyện xảy ra | File phải sửa | File KHÔNG phải sửa |
| --- | --- | --- |
| đổi URL `/products` thành `/v2/products` | `routes/` | services, models |
| shop đổi luật "miễn phí ship từ 50" | `services.py` | routes, models |
| đổi từ PostgreSQL trên máy sang Neon | `.env` (`DATABASE_URL`) | **mọi file code** |
| thêm một cột vào bảng | `models.py` + một migration mới | routes ít khi phải sửa |

Đây gọi là **tách mối quan tâm** (separation of concerns). Nó là nền tảng của gần như mọi kiến trúc phần mềm.

## 4. Vì sao chọn cách này (và không chọn cách khác)
| Lựa chọn | Mô tả | Hợp khi | Vì sao (chưa) chọn |
| --- | --- | --- | --- |
| **Chia theo tầng** ✅ | `routes/`, `services`, `models` chung cho cả app | app nhỏ đến vừa, 1-3 dev, ít khu vực | **đang dùng.** Đơn giản, đúng theo hướng dẫn "Bigger Applications" của FastAPI, ai mới vào cũng hiểu ngay |
| Chia theo tính năng | `products/` (router + models + service), `auth/`, `orders/`... mỗi khu vực một thư mục | app lớn, nhiều khu vực, nhiều team | **sẽ chuyển sang** khi có từ khoảng 4-5 khu vực (dự kiến Sprint 3: products, auth, cart, orders, payments). Các team FastAPI có kinh nghiệm khuyên cách này cho app lớn |
| Clean / Hexagonal architecture | lõi nghiệp vụ hoàn toàn tách khỏi framework và database, mọi thứ qua interface | hệ thống lớn, sống lâu năm, hay đổi hạ tầng | **chưa:** nhiều lớp trừu tượng làm chậm việc học và phát triển ở quy mô này |
| Microservices | mỗi khu vực là một service riêng, deploy riêng | công ty lớn, nhiều team độc lập | **không:** chưa cần mà chi phí vận hành rất cao |

**Nguyên tắc chọn:** dùng kiến trúc **đơn giản nhất mà vẫn giữ được các tầng tách nhau**. Chỉ chuyển sang kiến trúc phức tạp hơn khi có **vấn đề thật** (file quá dài, hay sửa nhầm chỗ, nhiều người đụng cùng một file), không chuyển "cho chắc".

## 5. Các quy tắc team phải giữ
1. Route **không** viết SQL phức tạp hay luật kinh doanh. Khi một route có quá ~15 dòng logic, chuyển phần đó sang `services.py`.
2. Service **không** dùng `HTTPException`. Service raise lỗi Python thường (ví dụ `OutOfStock`), route đổi lỗi đó thành mã HTTP.
3. Chỉ `config.py` đọc biến môi trường. Chỉ `db.py` tạo kết nối database.
4. Mọi thay đổi cấu trúc database đều đi qua **migration**. Không sửa database bằng tay.
5. Test chia theo khu vực (`test_products.py`, `test_auth.py`), dùng chung phần chuẩn bị trong `conftest.py`.

## 6. Câu phỏng vấn
**"Kể về kiến trúc dự án của bạn."** → "API FastAPI chia 3 tầng: routes chỉ lo HTTP, services chứa luật kinh doanh, models + session lo database PostgreSQL, có migration bằng Alembic. Phụ thuộc đi một chiều, nên đổi database hay đổi URL chỉ đụng tới một tầng. Khi app có thêm giỏ hàng, đơn hàng, thanh toán, tôi sẽ chuyển sang chia thư mục theo tính năng."

Tài liệu: [FastAPI: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) · [FastAPI best practices (zhanymkanov)](https://github.com/zhanymkanov/fastapi-best-practices)
