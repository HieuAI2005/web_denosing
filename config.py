import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    DENOISED_FOLDER = os.path.join(BASE_DIR, 'static', 'denoised')

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

    MAX_FILE_SIZE = 20 * 1024 * 1024 # bytes

    # Secret key cho Flask session (cần thiết cho production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here'

    FILE_LIFESPAN_HOURS = 24