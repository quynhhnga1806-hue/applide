"""SMART WASTE - lớp tích hợp TensorFlow/Keras.

Đặt model đã huấn luyện tại:
    static/models/waste_model.h5

Model được giả định trả về 5 xác suất theo thứ tự:
    Giấy, Hữu cơ, Kim loại, Nhựa, Rác khác

Nếu chưa có file model hoặc máy chưa cài TensorFlow, project vẫn chạy ở chế độ
DEMO_FALLBACK để sinh viên có thể kiểm tra toàn bộ luồng upload -> API -> UI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "static" / "models" / "waste_model.h5"

ALLOWED_LABELS = ["Giấy", "Hữu cơ", "Kim loại", "Nhựa", "Rác khác"]

LABEL_DETAILS = {
    "Giấy": {
        "bin": "THÙNG RÁC TÁI CHẾ",
        "guidance": "Gấp gọn giấy sạch, bỏ ghim và tách khỏi giấy bị dính dầu mỡ trước khi tái chế.",
        "icon": "▤",
        "accent": "paper",
    },
    "Hữu cơ": {
        "bin": "THÙNG RÁC HỮU CƠ",
        "guidance": "Tách riêng thức ăn thừa, rau củ và phần dễ phân hủy; hạn chế để lẫn túi nilon.",
        "icon": "✿",
        "accent": "organic",
    },
    "Kim loại": {
        "bin": "THÙNG RÁC TÁI CHẾ",
        "guidance": "Làm sạch lon/hộp kim loại và ép gọn nếu an toàn trước khi đưa vào thùng tái chế.",
        "icon": "⌁",
        "accent": "metal",
    },
    "Nhựa": {
        "bin": "THÙNG RÁC TÁI CHẾ",
        "guidance": "Rửa sạch và ép dẹt chai/lọ nhựa trước khi phân loại nếu phù hợp.",
        "icon": "♻",
        "accent": "plastic",
    },
    "Rác khác": {
        "bin": "THÙNG RÁC KHÁC",
        "guidance": "Kiểm tra hướng dẫn thu gom tại địa phương đối với vật liệu khó tái chế hoặc không xác định.",
        "icon": "◌",
        "accent": "other",
    },
}

_model: Any = None
_model_loaded = False


def _load_model() -> Any:
    """Lazy-load Keras để app khởi động được cả khi TensorFlow chưa cài."""
    global _model, _model_loaded
    if _model_loaded:
        return _model

    _model_loaded = True
    if not MODEL_PATH.exists():
        return None

    try:
        from tensorflow.keras.models import load_model

        _model = load_model(MODEL_PATH)
    except Exception:
        # Log chi tiết sẽ được ghi từ app khi classify_image gặp lỗi; fallback vẫn hoạt động.
        _model = None
    return _model


def _fallback_prediction(image_path: Path) -> tuple[str, float]:
    """Kết quả minh họa theo đúng mẫu giao diện, không giả vờ là model thật.

    Đây chỉ là fallback để UI có thể chạy khi chưa được cung cấp model h5.
    Khi có waste_model.h5 hợp lệ, hàm classify_image sẽ ưu tiên model thật.
    """
    return "Nhựa", 94.52


def classify_image(image_path: str | Path) -> dict[str, Any]:
    """Dự đoán ảnh và trả về payload thân thiện với frontend."""
    path = Path(image_path)
    model = _load_model()

    if model is not None:
        image = Image.open(path).convert("RGB")
        input_shape = getattr(model, "input_shape", None)
        height, width = 224, 224
        if isinstance(input_shape, tuple) and len(input_shape) >= 3:
            height = int(input_shape[1] or height)
            width = int(input_shape[2] or width)

        image = image.resize((width, height))
        import numpy as np

        array = np.asarray(image, dtype="float32") / 255.0
        probabilities = model.predict(np.expand_dims(array, axis=0), verbose=0)[0]
        probabilities = np.asarray(probabilities).reshape(-1)
        if len(probabilities) != len(ALLOWED_LABELS):
            raise ValueError(
                f"Model cần trả về {len(ALLOWED_LABELS)} lớp, nhận được {len(probabilities)} lớp."
            )
        winner_index = int(probabilities.argmax())
        label = ALLOWED_LABELS[winner_index]
        confidence = float(probabilities[winner_index]) * 100
    else:
        label, confidence = _fallback_prediction(path)

    return {
        "label": label,
        "confidence": round(confidence, 2),
        **LABEL_DETAILS[label],
        "is_fallback": model is None,
    }
