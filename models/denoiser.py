from imageio import imread
import numpy as np
import cv2
from models.model import DnCNN
import tensorflow as tf 
from models.utils import denormalize, normalize

MODEL_PATH = '/home/hiwe/project/app/models/weights/DnCNN_Default_SIDD_20211113-160850.h5'

def denoise_image(input_image_path):
    try:
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)

        model = DnCNN().get_model()
        model.load_weights(MODEL_PATH)

        img = imread(input_image_path)
        h, w, c = img.shape
        patch_size = 50
        stride = 50 

        padded_h = (h + patch_size - 1) // patch_size * patch_size
        padded_w = (w + patch_size - 1) // patch_size * patch_size
        padded_img = np.zeros((padded_h, padded_w, c), dtype=img.dtype)
        padded_img[:h, :w, :] = img

        output_img = np.zeros_like(padded_img)

        for i in range(0, padded_h, stride):
            for j in range(0, padded_w, stride):
                patch = padded_img[i:i+patch_size, j:j+patch_size, :]
                if patch.shape[0] != patch_size or patch.shape[1] != patch_size:
                    pad_patch = np.zeros((patch_size, patch_size, c), dtype=patch.dtype)
                    pad_patch[:patch.shape[0], :patch.shape[1], :] = patch
                    patch = pad_patch

                input_tensor = normalize(patch).reshape(1, patch_size, patch_size, 3).astype(np.float32)
                denoised_patch = model.predict(input_tensor)
                denoised_patch = np.squeeze(denoised_patch)
                denoised_patch = denormalize(denoised_patch)

                output_img[i:i+patch_size, j:j+patch_size, :] = denoised_patch

        result = output_img[:h, :w, :]
        result = np.clip(result, 0, 255).astype(np.uint8)

        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

        return result_bgr

    except Exception as e:
        print(f"Error in denoise_image function: {e}")
        return None
