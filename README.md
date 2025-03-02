# Ucademic
Backend cho dự án Ucademic - Web học online


## Cài đặt
Yêu cầu cài đặt: Python 3.10+
- Bước 1: Clone repository về máy, mở folder trong VSCode rồi mở Terminal
- Bước 2: Tạo 1 virtual enviroment mới: `python -m venv .venv`
- Bước 3: Activate virtual enviroment vừa tạo:
  - Với Windows:
    - `Set-ExecutionPolicy Unrestricted -Scope Process`
    - `.venv\Scripts\Activate.ps1`
  - Với Linux/macOS:
    - `source .venv/bin/activate`
  - Có thể kiểm tra virtual enviroment đã active chưa bằng lệnh sau (Nếu đường dẫn trả về nằm trong thư mục hiện tại thì thành công):
    - Window: `Get-Command python`
    - Linux/macOS: `which python`
- Bước 4: Cập nhật pip: `python -m pip install --upgrade pip`
- Bước 5 (Optional): Thêm .gitignore cho venv: `echo "*" > .venv/.gitignore`
- Bước 6: Cài đặt các thư viện cần thiết: `pip install -r requirements.txt`


## Run
Sử dụng lệnh `fastapi dev main.py` để khởi chạy server. Server sẽ chạy trên http://localhost:8000

Kiểm tra API Documentation tại http://localhost:8000/docs (Swagger UI) hoặc http://localhost:8000/redoc (ReDoc)
