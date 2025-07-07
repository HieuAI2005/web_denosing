# 🧼 Web Denoising Using DCNN (Swift, Restormer)

Ứng dụng web đơn giản sử dụng Flask kết hợp các mô hình Deep CNN (Swift, Restormer) để **khử nhiễu** và **tăng độ phân giải** cho ảnh và PDF.

## 🎯 Mục đích

- 🔧 Giảm nhiễu ảnh (image denoising)
- 🖼️ Cải thiện độ sắc nét ảnh
- 📄 Hỗ trợ cả file ảnh (`.png`, `.jpg`) và file PDF

---

## 🚀 Demo

<!-- Bạn có thể thêm ảnh screenshot ở đây -->
<!-- ![Demo](static/demo.gif) -->
(static/denoising_image.png)
---

## 🛠️ Công nghệ sử dụng

- [Flask](https://flask.palletsprojects.com/)
- [TensorFlow](https://www.tensorflow.org/)
- [OpenCV](https://opencv.org/)
- [pdf2image](https://pypi.org/project/pdf2image/)
- [image2pdf](https://pypi.org/project/image2pdf/)

## 📦 Cài đặt

```bash
# Clone repo
git clone https://github.com/HieuAI2005/web_denosing.git
cd web_denosing

# Cài dependencies
pip install -r requirements.txt

# Khởi chạy ứng dụng
python app.py
