// Bạn có thể thêm các logic JavaScript phức tạp hơn tại đây, ví dụ:
// - Hiển thị preview của file được chọn trước khi upload
// - Hiển thị spinner khi đang xử lý
// - Xử lý lỗi phía client

document.addEventListener('DOMContentLoaded', function() {
    // Example: Simple console log when page loads
    console.log('AI Denoising System loaded.');

    // Auto-dismiss Bootstrap alerts after a few seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Tự động đóng sau 5 giây
    });
});