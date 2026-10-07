# SMART WASTE – PHÂN LOẠI RÁC THÔNG MINH

Website demo Flask + HTML/CSS/JavaScript + TensorFlow/Keras cho bài toán nhận diện rác bằng ảnh.

## 1. Cấu trúc project

```text
smart-waste/
├── app.py                         # Flask server và API /api/classify
├── model_ai.py                    # Nạp waste_model.h5 và chạy dự đoán Keras
├── requirements.txt               # Thư viện Python
├── manus-routes.json              # Khai báo route trang chủ
├── README.md
├── templates/
│   └── index.html                 # Giao diện trang chính
└── static/
    ├── css/
    │   └── style.css              # Thiết kế responsive
    ├── js/
    │   └── app.js                 # Camera, upload, preview và gọi API
    ├── uploads/                   # Ảnh upload tạm thời
    └── models/
        ├── waste_model.h5         # Model thật: bạn chép file vào đây
        └── README.txt
```

Không có database, đăng nhập, đăng ký, điểm số, lịch sử hay trang quản trị.

## 2. Luồng hoạt động

1. Người dùng bấm **CHỤP ẢNH** hoặc **TẢI ẢNH LÊN**.
2. JavaScript hiển thị preview và gửi ảnh bằng `multipart/form-data` tới `POST /api/classify`.
3. Flask lưu ảnh tạm trong `static/uploads/`.
4. `model_ai.py` nạp `static/models/waste_model.h5` bằng TensorFlow/Keras, resize ảnh và lấy lớp có xác suất cao nhất.
5. Flask trả JSON gồm loại rác, độ tin cậy, thùng rác đề xuất và hướng dẫn.
6. JavaScript render card **KẾT QUẢ PHÂN LOẠI**.

Nếu chưa có `waste_model.h5` hoặc TensorFlow chưa cài, ứng dụng chạy **DEMO_FALLBACK** và hiển thị đúng mẫu minh họa **Nhựa – 94.52% – Thùng rác tái chế**. Đây chỉ để kiểm tra UI và luồng upload; khi đưa model thật vào đúng thư mục, code sẽ tự ưu tiên TensorFlow.

## 3. Chạy trên Windows bằng VS Code

### Bước 1: Cài phần mềm

- Cài Python 3.10 (khuyến nghị nếu muốn chạy TensorFlow native trên Windows).
- Cài VS Code và extension **Python** của Microsoft.
- Mở thư mục `smart-waste` bằng VS Code: **File → Open Folder**.

### Bước 2: Tạo môi trường ảo

Mở Terminal trong VS Code (**Terminal → New Terminal**) và chạy:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn script, chạy một lần:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Sau đó activate lại:

```powershell
.venv\Scripts\Activate.ps1
```

Nếu terminal hiển thị `(.venv)` ở đầu dòng là đã đúng.

### Bước 3: Cài thư viện cơ bản

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4: Cài TensorFlow để dùng model thật (tùy chọn)

Với Python 3.10 native trên Windows, bỏ dấu `#` trước dòng `tensorflow-cpu==2.10.1` trong `requirements.txt`, rồi chạy:

```powershell
pip install tensorflow-cpu==2.10.1
```

Hoặc cài trực tiếp sau khi cài dependencies cơ bản:

```powershell
pip install tensorflow-cpu==2.10.1
```

> Nếu chỉ muốn xem giao diện và test upload, có thể chưa cài TensorFlow. Ứng dụng vẫn chạy bằng chế độ demo dự phòng.

### Bước 5: Đặt model vào đúng thư mục

Chép file model Keras vào:

```text
static/models/waste_model.h5
```

Model cần trả về **5 xác suất** theo đúng thứ tự:

1. `Giấy`
2. `Hữu cơ`
3. `Kim loại`
4. `Nhựa`
5. `Rác khác`

Nếu model của bạn dùng thứ tự khác, sửa danh sách `ALLOWED_LABELS` trong `model_ai.py` để khớp.

### Bước 6: Chạy Flask

```powershell
python app.py
```

Mở trình duyệt tại:

```text
http://127.0.0.1:5000
```

Dừng server bằng `Ctrl + C`.

## 4. Test nhanh API (không bắt buộc)

Sau khi server đang chạy, có thể dùng PowerShell:

```powershell
curl.exe -X POST -F "image=@duong-dan-den-anh.jpg" http://127.0.0.1:5000/api/classify
```

Kiểm tra server:

```text
http://127.0.0.1:5000/health
```

## 5. Một số lỗi thường gặp

### `No module named flask`

Đảm bảo terminal đang có `(.venv)`, sau đó chạy:

```powershell
pip install -r requirements.txt
```

### Không mở được camera

- Trên điện thoại, mở bằng HTTPS hoặc localhost được trình duyệt cho phép.
- Trên máy tính, nút **CHỤP ẢNH** sẽ mở webcam nếu trình duyệt hỗ trợ thuộc tính `capture`; nếu không, có thể chọn ảnh từ hộp thoại file.
- Hãy cấp quyền camera cho trình duyệt.

### Kết quả hiển thị chế độ demo

Đây là bình thường khi chưa có `static/models/waste_model.h5` hoặc TensorFlow chưa cài. Chép model thật vào đúng vị trí và khởi động lại server.

## 6. Các file cần chỉnh khi muốn thay model

Thông thường chỉ cần:

- `static/models/waste_model.h5`: file model Keras.
- `model_ai.py`: kích thước input nếu model không dùng 224×224, và thứ tự 5 nhãn nếu khác.

Frontend không cần sửa nếu API vẫn trả các key: `label`, `confidence`, `bin`, `guidance`, `icon`, `is_fallback`.
