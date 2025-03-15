# Ucademic
Backend cho dự án Ucademic - Web học online


## Công nghệ
- [FastAPI](https://fastapi.tiangolo.com) - Framework cho ứng dụng web trên Python
- [SQLite3](https://www.sqlite.org) - Database 
- [SQLModel](https://sqlmodel.tiangolo.com) - ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration


## Cài đặt
Yêu cầu cài đặt: Python 3.10+ 


```shell
git clone https://github.com/Silwee/ucademic.git
cd ucademic
python -m venv .venv
```

Tiếp theo [Activate virtual environment](#Activate-virtual-environment)

Cài đặt các thư viện cần thiết

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> [!NOTE]
> Nếu gặp phải FastAPIError hoặc bất kỳ lỗi nào khác khi khởi chạy server, 
thử chạy lại `pip install -r requirements.txt` trong terminal.


## Run
### Activate virtual environment
Chạy mỗi khi mở terminal mới. Bỏ que nếu terminal đã kích hoạt venv (hiển thị (.venv) trước mỗi dòng lệnh)
- Windows Powershell

  ```shell
  Set-ExecutionPolicy Unrestricted -Scope Process
  .venv\Scripts\Activate.ps1
  ```

- Window Bash (cmd)

  ```shell
  source .venv/Scripts/activate
  ```

- Linux/macOS

  ```sh
  source .venv/bin/activate
  ```

### Cập nhật database
Chạy sau mỗi lần git pull
```shell
alembic upgrade head
```

### Khởi chạy server
```
fastapi dev main.py
```

Server sẽ chạy trên http://localhost:8000

Kiểm tra API Documentation tại http://localhost:8000/docs (Swagger UI) hoặc http://localhost:8000/redoc (ReDoc)
